const { default: mongoose } = require("mongoose");

const dbConnect = () => {
  try {
    const conn = mongoose.connect("mongodb+srv://PDS:PDS2024@pds.mywkn.mongodb.net/?retryWrites=true&w=majority&appName=PDS");
    console.log("Database Connected Successfully");
  } catch (error) {
    console.log("DAtabase error");
  }
};
module.exports = dbConnect;
