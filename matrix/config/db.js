const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.DB);
    console.log(`✅ | Conexão com o MongoDB estabelecida com sucesso`.green);
  } catch (error) {
    console.log(`❌ | Conexão com o MongoDB falhou`.red, error);
    process.exit(1);
  }
};

module.exports = connectDB;
