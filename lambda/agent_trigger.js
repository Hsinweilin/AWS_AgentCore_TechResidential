/**
 * AWS Lambda function for triggering Bedrock Agent with browser automation
 */

const AWS = require('aws-sdk');
const bedrock = new AWS.BedrockRuntime();
const s3 = new AWS.S3();
const secretsManager = new AWS.SecretsManager();
const ses = new AWS.SES();

/**
 * Lambda handler function triggered by EventBridge scheduler
 */
exports.handler = async (event) => {
  console.log('Received event:', JSON.stringify(event, null, 2));
  
  try {
    // Extract parameters from the event
    const taskId = event.taskId;
    const userId = event.userId;
    const urlSecretName = event.urlSecretName;
    const credentialsSecretName = event.credentialsSecretName;
    const promptFileKey = event.promptFileKey;
    const outputBucket = event.outputBucket;
    const notificationEmail = event.notificationEmail;
    
    // Get URL from Secrets Manager
    const urlSecret = await secretsManager.getSecretValue({
      SecretId: urlSecretName
    }).promise();
    const websiteUrl = JSON.parse(urlSecret.SecretString).url;
    
    // Get credentials from Secrets Manager
    const credentialsSecret = await secretsManager.getSecretValue({
      SecretId: credentialsSecretName
    }).promise();
    const credentials = JSON.parse(credentialsSecret.SecretString);
    
    // Get prompt file from S3
    const promptFileObject = await s3.getObject({
      Bucket: process.env.PROMPT_BUCKET,
      Key: promptFileKey
    }).promise();
    const promptInstructions = promptFileObject.Body.toString('utf-8');
    
    // Prepare agent input
    const agentInput = {
      taskId,
      websiteUrl,
      username: credentials.username,
      password: credentials.password,
      instructions: promptInstructions
    };
    
    // Invoke Bedrock agent
    const agentResult = await invokeBedrockAgent(agentInput);
    
    // If document was downloaded successfully
    if (agentResult.documentContent && agentResult.documentName) {
      // Save document to S3
      const documentKey = `${userId}/${taskId}/${agentResult.documentName}`;
      await s3.putObject({
        Bucket: outputBucket,
        Key: documentKey,
        Body: Buffer.from(agentResult.documentContent, 'base64'),
        ContentType: agentResult.documentContentType || 'application/pdf'
      }).promise();
      
      // Send notification email
      await sendNotificationEmail(notificationEmail, {
        taskId,
        documentName: agentResult.documentName,
        documentUrl: `https://${outputBucket}.s3.amazonaws.com/${documentKey}`,
        executionTime: new Date().toISOString()
      });
      
      return {
        statusCode: 200,
        body: JSON.stringify({
          message: 'Document retrieved and saved successfully',
          documentKey
        })
      };
    } else {
      throw new Error('Document retrieval failed: ' + (agentResult.error || 'Unknown error'));
    }
  } catch (error) {
    console.error('Error:', error);
    
    // Send failure notification if email is provided
    if (event.notificationEmail) {
      await sendFailureNotification(event.notificationEmail, {
        taskId: event.taskId,
        error: error.message
      });
    }
    
    return {
      statusCode: 500,
      body: JSON.stringify({
        message: 'Error executing browser automation task',
        error: error.message
      })
    };
  }
};

/**
 * Invoke Bedrock agent with browser capabilities
 */
async function invokeBedrockAgent(agentInput) {
  const agentId = process.env.BEDROCK_AGENT_ID;
  const agentAliasId = process.env.BEDROCK_AGENT_ALIAS_ID;
  
  const payload = {
    agentId,
    agentAliasId,
    sessionId: `session-${agentInput.taskId}`,
    inputText: `Perform browser automation with the following parameters:
      URL: ${agentInput.websiteUrl}
      Instructions: ${agentInput.instructions}`,
    enableTrace: true
  };
  
  // Add credentials as session attributes (will be accessible to the agent but not in logs)
  payload.sessionState = {
    sessionAttributes: {
      username: agentInput.username,
      password: agentInput.password
    }
  };
  
  const response = await bedrock.invokeAgent(payload).promise();
  
  // Process agent response
  try {
    const result = JSON.parse(response.completion);
    return {
      documentContent: result.documentContent,
      documentName: result.documentName,
      documentContentType: result.documentContentType,
      executionDetails: result.executionDetails
    };
  } catch (error) {
    console.error('Error parsing agent response:', error);
    return {
      error: 'Failed to parse agent response'
    };
  }
}

/**
 * Send notification email with document link
 */
async function sendNotificationEmail(recipientEmail, details) {
  const params = {
    Destination: {
      ToAddresses: [recipientEmail]
    },
    Message: {
      Body: {
        Html: {
          Data: `
            <h1>Document Retrieval Completed</h1>
            <p>Your scheduled document retrieval task (ID: ${details.taskId}) has completed successfully.</p>
            <p><strong>Document:</strong> ${details.documentName}</p>
            <p><strong>Executed at:</strong> ${details.executionTime}</p>
            <p>You can download your document using <a href="${details.documentUrl}">this link</a>.</p>
            <p>This link will expire in 7 days.</p>
          `
        },
        Text: {
          Data: `
            Document Retrieval Completed
            
            Your scheduled document retrieval task (ID: ${details.taskId}) has completed successfully.
            
            Document: ${details.documentName}
            Executed at: ${details.executionTime}
            
            You can download your document at: ${details.documentUrl}
            
            This link will expire in 7 days.
          `
        }
      },
      Subject: {
        Data: `Document Retrieval Completed - ${details.documentName}`
      }
    },
    Source: process.env.SENDER_EMAIL
  };
  
  return ses.sendEmail(params).promise();
}

/**
 * Send failure notification email
 */
async function sendFailureNotification(recipientEmail, details) {
  const params = {
    Destination: {
      ToAddresses: [recipientEmail]
    },
    Message: {
      Body: {
        Html: {
          Data: `
            <h1>Document Retrieval Failed</h1>
            <p>Your scheduled document retrieval task (ID: ${details.taskId}) has failed.</p>
            <p><strong>Error:</strong> ${details.error}</p>
            <p>Please check your automation settings and try again.</p>
          `
        },
        Text: {
          Data: `
            Document Retrieval Failed
            
            Your scheduled document retrieval task (ID: ${details.taskId}) has failed.
            
            Error: ${details.error}
            
            Please check your automation settings and try again.
          `
        }
      },
      Subject: {
        Data: `Document Retrieval Failed - Task ${details.taskId}`
      }
    },
    Source: process.env.SENDER_EMAIL
  };
  
  return ses.sendEmail(params).promise();
}
