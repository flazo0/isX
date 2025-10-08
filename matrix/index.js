console.clear();
require("dotenv").config();

const express = require("express");
const session = require("express-session");
const colors = require("colors");
const helmet = require("helmet");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const AdmZip = require("adm-zip");
const crypto = require("crypto");
const mkdirp = require("mkdirp");
// const rateLimit = require("express-rate-limit");
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

// ----------- PUBLIC  ----------- 
app.use(express.static("public"));

// ----------- UPLOADS -----------
const PUBLIC_DIR = path.join(__dirname, "public");
const UPDATES_DIR = path.join(PUBLIC_DIR, "updates");
mkdirp.sync(UPDATES_DIR);

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, UPDATES_DIR),
  filename: (req, file, cb) => {
    const ts = Date.now();
    cb(null, `${ts}_${file.originalname.replace(/[^\w.\-]/g, "_")}`);
  },
});
const upload = multer({ storage });

// ----------- ROTAS -----------
app.use("/api/v1", require("./routes/v1"));

app.post("/upload-commands", upload.single("commands_zip"), (req, res) => {
  if (!req.file) return res.status(400).json({ ok: false, error: "Nenhum arquivo enviado" });

  return res.json({
    ok: true,
    message: "Zip enviado com sucesso",
    zipFile: `/public/updates/${req.file.filename}`
  });
});

// Lista todos os zips disponíveis
app.get("/commands-list", (req, res) => {
  const files = fs.readdirSync(UPDATES_DIR)
    .filter(f => f.endsWith(".zip"))
    .map(f => ({ name: f, url: `/updates/${f}` }));
  res.json({ ok: true, zips: files });
});


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
