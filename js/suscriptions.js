const { Client, LocalAuth, MessageAck } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const utils = require('./utils');

const archivoSuscriptores = 'suscriptores.json';

let suscriptores = utils.database(archivoSuscriptores);

// Crear una nueva instancia del cliente de WhatsApp
const client = new Client({
    authStrategy: new LocalAuth()  // Esto guardará la sesión de WhatsApp para que no tengas que escanear el QR cada vez
});

// Generar y mostrar el código QR en la terminal
client.on('qr', (qr) => {
    qrcode.generate(qr, { small: true });
});

// Indica cuando el cliente está listo para ser utilizado
client.on('ready', () => {
    console.log('Cliente está listo para ser usado!');
});

client.on('message', async message => {
    if (message.body === '/help'){
        utils.help(message)
    }
    else if (message.body === '/lg') {
        suscriptores[message.from] = true;
        utils.guardarSuscriptores(archivoSuscriptores, suscriptores);
    }
    else if (suscriptores[message.from] === true){
        // Verificar si el comando /s tiene al menos dos partes y el argumento no está vacío

        const contact = await message.getContact();
        const contactName = contact.pushname || contact.notifyName || 'Undefined';
        console.log('');
        console.log(`by: ${contactName}`);
        console.log('Command:',message.body);

        const partes = message.body.split(' ');
        const numero = message.body.split(' ')[1];

        if (partes.length < 2 || partes[1].trim() === '') {
            // Manejar el caso en que no se proporciona el argumento
            message.reply(`Respuesta: command ${partes[0]} requiere suministro`);
            console.error(`ReponsePython: command ${partes[0]} requiere suministro`);
            return;
        }
        
        if (message.body.startsWith('/s ')) {
            // const numero = message.body.split(' ')[1];
            
            exec(`python3 /home/kimshizi/Documents/test/py/Utils.py ${numero} --mode apiUrl`, (error, stdout, stderr) => {
                if (error) {
                    console.error(`Error ejecutando el script: ${error.message}`);
                    return;
                }
                if (stderr) {
                    console.error(`Error estándar: ${stderr}`);
                    return;
                }
                message.reply(`Respuesta: ${stdout}`);
                console.log(`ReponsePython: ${stdout}`);
            });
        }

        if (message.body.startsWith('/d ')) {
            const numero = message.body.split(' ')[1];
            exec(`python3 /home/kimshizi/Documents/test/py/Utils.py ${numero} --mode apiDoc`, (error, stdout, stderr) => {
                if (error) {
                    console.error(`Error ejecutando el script: ${error.message}`);
                    return;
                }
                if (stderr) {
                    console.error(`Error estándar: ${stderr}`);
                    return;
                }

                if (stdout.trim() === 'False') {
                    message.reply(`Suministro No Existe`);

                } else {
                    if (stdout.trim().endsWith('.pdf')){
                    const pdf = MessageMedia.fromFilePath(`${__dirname}/py/pdf/${numero}.pdf`);
                    message.reply(`Respuesta: ${stdout.trim()}`, undefined, { media: pdf, quotedMessageId: message.id._serialized });
                    }

                    else{
                        message.reply(`Respuesta: ${stdout.trim()}`);
                    };
                }
                console.log(`ReponsePython: ${stdout}`);
            });
        }
    }

});

// Iniciar el cliente
client.initialize();
