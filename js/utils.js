const {exec} = require('child_process');
const fs = require('fs');
const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');

function help(message) {
    const banner = 'Bienvenido al bot:\n\ncomandos:\n\n/lg suscribir al bot\n/s obtener url\n/d obtener pdf';
    message.reply(banner);
}

// Función para guardar suscriptores en un archivo JSON
function guardarSuscriptores(filesuscription, suscriptores, message) {
    fs.writeFileSync(filesuscription, JSON.stringify(suscriptores, null, 2));
    message.reply('Usuario registrado');
}

// Función para cargar suscriptores desde un archivo JSON
function database(filesuscription) {
    let suscriptores = {};
    if (fs.existsSync(filesuscription)) {
        suscriptores = JSON.parse(fs.readFileSync(filesuscription, 'utf-8'));
    }
    return suscriptores;
}

function argument_management(partes){
    message.reply(`Respuesta: command ${partes[0]} requiere suministro`);
    console.error(`ReponsePython: command ${partes[0]} requiere suministro`);
    return;
}

function sendfile(evalue,numero,message){


    if (evalue.trim() === 'suministro no existe en base de datos') {
        message.reply(`Suministro No Existe`);

    } else if (evalue.trim().endsWith('.pdf')) {
        const pdf = MessageMedia.fromFilePath(`${__dirname}/../py/pdf/${numero}.pdf`);
        message.reply(`Respuesta: ${evalue}`, undefined, { media: pdf, quotedMessageId: message.id._serialized });
        console.log(`ReponsePython: envio existoso ${evalue}`);
    }

        // else{
        //     message.reply(`Respuesta: ${stdout.trim()}`);
        // };
    }


    // console.log(`ReponsePython: ${stdout}`);
// }

function execution_cmd(suministro, mode, message) {
    // Validación básica de parámetros
    if (typeof suministro !== 'string' || typeof mode !== 'string') {
        throw new Error('Los parámetros suministro y mode deben ser cadenas');
    }

    return new Promise((resolve, reject) => {
        exec(`python3 /home/kimshizi/Documents/test/py/Utils.py ${suministro} --mode ${mode}`, (error, stdout, stderr) => {
            if (error) {
                console.error(`Error ejecutando el script: ${error.message}`);
                reject(error);
                return;
            }
            if (stderr) {
                console.error(`Error estándar: ${stderr}`);
                reject(stderr);
                return;
            }
            resolve(stdout);
        });
    });
}

module.exports = {
    help,
    guardarSuscriptores,
    database,
    argument_management,
    execution_cmd,
    sendfile
};
