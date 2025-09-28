console.clear();
require('dotenv').config();

const express = require('express');
const session = require('express-session');
const colors = require('colors');
const path = require('path');
const helmet = require('helmet');
// const rateLimit = require('express-rate-limit');
const mongoSanitize = require('express-mongo-sanitize');
const xss = require('xss-clean');
const cors = require('cors');
const morgan = require('morgan');

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
  origin: process.env.ALLOWED_ORIGIN || '*',
  methods: ['GET','POST'],
  credentials: true
}));

// Logger de requests
app.use(morgan('dev'));

// ----------- BODY PARSERS E SESSÃO -----------
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

app.use(session({
  secret: process.env.SESSION,
  resave: false,
  saveUninitialized: true,
  cookie: {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
    maxAge: 24 * 60 * 60 * 1000
  }
}));

// ----------- VIEW ENGINE -----------
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

// ----------- ROTAS -----------

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
  console.log(`\n🔥 | PAINEL WEB RODANDO EM ${process.env.LINK || "http://localhost:" + PORT}/`.green);
});
