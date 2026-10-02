const express = require("express");
const path = require("path");

const app = express();

app.use(express.static(__dirname));

const PORT = 3000;

app.listen(PORT, () => {
    console.log(`Frontend running on http://localhost:${PORT}`);
});
