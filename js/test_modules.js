const utils = require('./utils');
const fs = require('fs');

// Definir la ubicación del archivo de suscriptores
const archivoSuscriptores = 'suscriptores.json';

// Cargar los suscriptores desde el archivo al iniciar
let suscriptores = utils.database(archivoSuscriptores);

if (suscriptores['915985158'] === true){
    console.log('usuario suscrito')
}
else{
    console.log('usuario no suscrito')
}

// // Agregar un nuevo suscriptor (ejemplo)
// suscriptores['915985153'] = true;

// // Guardar los suscriptores actualizados en el archivo
// utils.guardarSuscriptores(archivoSuscriptores, suscriptores);

// // Puedes ahora manejar los comandos usando los datos en `suscriptores`

