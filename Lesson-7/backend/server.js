require("dotenv").config();

const express = require("express");
const cors = require("cors");

const {
  BedrockAgentRuntimeClient,
  InvokeAgentCommand
} = require("@aws-sdk/client-bedrock-agent-runtime");

const app = express();

app.use(cors());
app.use(express.json());

const client =
  new BedrockAgentRuntimeClient({
    region: process.env.AWS_REGION
  });

app.post("/chat", async (req, res) => {

  try {

    const command =
      new InvokeAgentCommand({
        agentId: process.env.AGENT_ID,
        agentAliasId: process.env.AGENT_ALIAS_ID,
        sessionId: Date.now().toString(),
        inputText: req.body.message
      });

    const response =
      await client.send(command);

    let answer = "";

    for await (
      const chunk of response.completion
    ) {

      if (chunk.chunk?.bytes) {

        answer +=
          Buffer
            .from(chunk.chunk.bytes)
            .toString("utf8");
      }
    }

    res.json({
      success: true,
      answer
    });

  } catch (err) {

    console.error(err);

    res.status(500).json({
      success: false,
      error: err.message
    });

  }

});

app.listen(
  process.env.PORT,
  () => {
    console.log(
      `Server running on port ${process.env.PORT}`
    );
  }
);