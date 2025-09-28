console.clear();
require("dotenv").config();

const express = require("express");
const session = require("express-session");
const colors = require("colors");
const helmet = require("helmet");
// const rateLimit = require("express-rate-limit");
const mongoSanitize = require("express-mongo-sanitize");
const xss = require("xss-clean");
const cors = require("cors");
const morgan = require("morgan");
const connectDB = require("./config/db");

// ----------- CONECTANDO AO BANCO DE DADOS -----------
connectDB();

// ----------- INICIANDO EXPRESS -----------
const app = express();

// ----------- MIDDLEWARES DE SEGURANÇA -----------

// Proteção de headers HTTP
app.use(helmet());

// Limite de requisições
// const limiter = rateLimit({
//   windowMs: 15 * 60 * 1000, // 15 minutos
//   max: 100, // 100 requisições por IP
//   message: "Too many requests from this IP, please try again later."
// }); 
// app.use(limiter);

// Proteção contra NoSQL Injection
app.use(mongoSanitize());

// Proteção contra XSS
app.use(xss());

// CORS
app.use(cors({
  origin: process.env.ALLOWED_ORIGIN || "*",
  methods: ["GET","POST","PUT","DELETE"],
  credentials: true
}));

// Logger de requests
app.use(morgan("dev"));

// ----------- BODY PARSERS E SESSÃO -----------
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// ----------- ROTAS -----------
app.use("/api/v1", require("./routes/v1"));

// ----------- TRATAMENTO DE ERROS -----------

// 404
app.use((req, res, next) => res.status(404).json({
  errors: true,
  status: 404,
  messages: ["This page does not exist"]
}));

// Error handler genérico
app.use((err, req, res, next) => {
  console.error(err.stack.red);
  res.status(500).json({
    errors: true,
    status: 500,
    messages: ["Internal Server Error"]
  });
});

// ----------- INICIANDO SERVIDOR -----------
const PORT = process.env.PORT || 80;
app.listen(PORT, () => {
  console.log(`\n🔥 | API RODANDO EM ${process.env.LINK || "http://localhost:" + PORT}/`.green);
});
