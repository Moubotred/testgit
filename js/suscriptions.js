const { Client, LocalAuth, MessageMedia } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const utils = require('./utils');
const fs = require('fs');

const Chance = require('chance');
const chance = new Chance();

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
        utils.guardarSuscriptores(archivoSuscriptores, suscriptores, message);
    }

    else if (suscriptores[message.from] === true && message.body.startsWith('/i') && message.hasMedia) {
        if (message.hasMedia) {
            const media = await message.downloadMedia();
            if (media) {
                // Guarda la imagen en el disco
                const fileName = chance.string({ length: 7, pool:'1234567'}) + '.jpg';
                fs.writeFileSync(`/home/kimshizi/Documents/test/py/tmp/${fileName}`, media.data, 'base64');

                const value = utils.execution_cmd(fileName,'apiImg',message)
                    .then(resultado=>{
                        if (resultado.trim().endsWith('.pdf')) {
                            const pdf = MessageMedia.fromFilePath(`/home/kimshizi/Documents/test/py/pdf/${resultado}`.trim());
                            message.reply(`Respuesta: ${resultado}`, undefined, { media: pdf, quotedMessageId: message.id._serialized });
                            console.log(`ReponsePython: envio existoso ${resultado}`);
                        }
                        // message.reply(`Respuesta: ${resultado}`);
                        // console.log(`ReponsePython: ${resultado}`);
                    })

                    .catch(error =>{
                        console.log(`ReponsePython: ${error}`);
                    })

            }
        }
    }

    else if (suscriptores[message.from] === true){
        // Verificar si el comando /s tiene al menos dos partes y el argumento no está vacío
        const contact = await message.getContact();
        const contactName = contact.pushname || contact.notifyName || 'Undefined';
        const partes = message.body.split(' ');
        const suministro = message.body.split(' ')[1];        

        // console.log(suministro);
        // if (partes.length < 2 || partes[1].trim() === '') {
            // utils.argument_management(partes,message)
        // }
        if (!isNaN(suministro) && suministro.length >= 1 && suministro.length <= 7) {

            console.log(`by: ${contactName}`);
            console.log('Command:',message.body);

            if (message.body.startsWith('/s ')) {
            
                const value = utils.execution_cmd(suministro,'apiUrl',message)
                    .then(resultado=>{
                        message.reply(`Respuesta: ${resultado}`);
                        console.log(`ReponsePython: ${resultado}`);
                    })
    
                    .catch(error =>{
                        console.log(`ReponsePython: ${error}`);
                    })
    
            }
    
            if (message.body.startsWith('/d ')) {
    
                const value = utils.execution_cmd(suministro,'apiDoc',message)
                    .then(resultado =>{
                        utils.sendfile(resultado,suministro,message)
                    })
    
                    .catch(error =>{
                        console.log(error);
                    })
            }
            
            // if (message.body.startsWith('/i') && message.hasMedia) {
            //     if (message.hasMedia) {
            //         const media = await message.downloadMedia();
            //         if (media) {
            //             // Guarda la imagen en el disco
            //             fs.writeFileSync('/home/kimshizi/Documents/test/py/tmp/over.jpg', media.data, 'base64');
            //             console.log('Imagen descargada');
            //         }
            //     }
            // }
                    
        }

    }

});

// Iniciar el cliente
client.initialize();
