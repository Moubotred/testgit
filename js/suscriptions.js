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
        utils.guardarSuscriptores(archivoSuscriptores, suscriptores, message);
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
    
                // console.log(value);
    
                // exec(`python3 /home/kimshizi/Documents/test/py/Utils.py ${suministro} --mode apiDoc`, (error, stdout, stderr) => {
                //     if (error) {
                //         console.error(`Error ejecutando el script: ${error.message}`);
                //         return;
                //     }
                //     if (stderr) {
                //         console.error(`Error estándar: ${stderr}`);
                //         return;
                //     }
    
                    
                    // if (stdout.trim() === 'False') {
                    //     message.reply(`Suministro No Existe`);
    
                    // } else {
                    //     if (stdout.trim().endsWith('.pdf')){
                    //     const pdf = MessageMedia.fromFilePath(`${__dirname}/py/pdf/${suministro}.pdf`);
                    //     message.reply(`Respuesta: ${stdout.trim()}`, undefined, { media: pdf, quotedMessageId: message.id._serialized });
                    //     }
    
                    //     else{
                    //         message.reply(`Respuesta: ${stdout.trim()}`);
                    //     };
                    // }
    
    
                    // console.log(`ReponsePython: ${stdout}`);
                    // }
                // );
            }
        }

        // if (message.body.startsWith('/s ')) {
            
        //     const value = utils.execution_cmd(suministro,'apiUrl',message)
        //         .then(resultado=>{
        //             message.reply(`Respuesta: ${resultado}`);
        //             console.log(`ReponsePython: ${resultado}`);
        //         })

        //         .catch(error =>{
        //             console.log(`ReponsePython: ${error}`);
        //         })

        // }

        // if (message.body.startsWith('/d ')) {

        //     const value = utils.execution_cmd(suministro,'apiDoc',message)
        //         .then(resultado =>{
        //             utils.sendfile(resultado,suministro,message)
        //         })

        //         .catch(error =>{
        //             console.log(error);
        //         })

        //     // console.log(value);

        //     // exec(`python3 /home/kimshizi/Documents/test/py/Utils.py ${suministro} --mode apiDoc`, (error, stdout, stderr) => {
        //     //     if (error) {
        //     //         console.error(`Error ejecutando el script: ${error.message}`);
        //     //         return;
        //     //     }
        //     //     if (stderr) {
        //     //         console.error(`Error estándar: ${stderr}`);
        //     //         return;
        //     //     }

                
        //         // if (stdout.trim() === 'False') {
        //         //     message.reply(`Suministro No Existe`);

        //         // } else {
        //         //     if (stdout.trim().endsWith('.pdf')){
        //         //     const pdf = MessageMedia.fromFilePath(`${__dirname}/py/pdf/${suministro}.pdf`);
        //         //     message.reply(`Respuesta: ${stdout.trim()}`, undefined, { media: pdf, quotedMessageId: message.id._serialized });
        //         //     }

        //         //     else{
        //         //         message.reply(`Respuesta: ${stdout.trim()}`);
        //         //     };
        //         // }


        //         // console.log(`ReponsePython: ${stdout}`);
        //         // }
        //     // );
        // }
    }

});

// Iniciar el cliente
client.initialize();
