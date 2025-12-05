import { Analytics } from "@vercel/analytics/next"
import { streamText } from "ai";

const result = streamText({
  model: "moonshotai/kimi-k2-thinking",
  prompt: "What is the history of the San Francisco Mission-style burrito?",
});
