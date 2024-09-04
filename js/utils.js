const fs = require('fs');

function help(message) {
    const banner = 'Bienvenido al bot:\n\ncomandos:\n\n/lg suscribir al bot\n/s obtener url\n/d obtener pdf';
    message.reply(banner);
}

// Función para guardar suscriptores en un archivo JSON
function guardarSuscriptores(filesuscription, suscriptores) {
    fs.writeFileSync(filesuscription, JSON.stringify(suscriptores, null, 2));
}

// Función para cargar suscriptores desde un archivo JSON
function database(filesuscription) {
    let suscriptores = {};
    if (fs.existsSync(filesuscription)) {
        suscriptores = JSON.parse(fs.readFileSync(filesuscription, 'utf-8'));
    }
    return suscriptores;
}

function Argument_Management(partes){
    message.reply(`Respuesta: command ${partes[0]} requiere suministro`);
    console.error(`ReponsePython: command ${partes[0]} requiere suministro`);
    return;
}

module.exports = {
    help,
    guardarSuscriptores,
    database
};
