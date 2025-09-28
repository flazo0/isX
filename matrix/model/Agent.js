// models/Agent.js
const mongoose = require("mongoose");

const AgentSchema = new mongoose.Schema({
  ipAddress: {
    type: String,
    required: true
  },
  hostname: {
    type: String,
    required: true
  },
  username: {
    type: String,
    default: "unknown"
  },
  operatingSystem: {
    type: String,
    default: "unknown"
  },
  architecture: {
    type: String,
    enum: ["x86", "x64", "arm", "AMD64", "unknown"],
    default: "unknown"
  },
  cpu: {
    model: { type: String, default: "unknown" },
    cores: { type: Number, default: 0 }
  },
  memory: {
    total: { type: Number, default: 0 }, // em MB
    free: { type: Number, default: 0 }
  },
  disk: {
    total: { type: Number, default: 0 }, // em GB
    free: { type: Number, default: 0 }
  },
  status: {
    type: String,
    enum: ["online", "offline", "idle", "busy", "error"],
    default: "offline"
  },
  returned: {
    type: String,
    default: false
  },
  lastActivity: {
    type: Date,
    default: Date.now
  },
  lastSeen: {
    type: Date,
    default: Date.now
  },
  lastCode: {
    type: Number,
    default: 0
  },
  commandQueue: [
    {
      commandId: { type: mongoose.Schema.Types.ObjectId, auto: true },
      command: { type: String, required: true },
      payload: { type: Object, default: {} },
      createdAt: { type: Date, default: Date.now },
      executed: { type: Boolean, default: false },
      executedAt: { type: Date },
      output: { type: String, default: "" }
    }
  ],
  logs: [
    {
      type: {
        type: String, // info, error, warning, event
        default: "info"
      },
      message: { type: String },
      createdAt: { type: Date, default: Date.now }
    }
  ],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model("Agent", AgentSchema);
