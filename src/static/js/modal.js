const editButtons = document.querySelectorAll('.btn');

// Añadir un evento de clic a cada botón
editButtons.forEach(button => {
    button.addEventListener('click', () => {
        const codigo = button.id.replace('btn-edit', ''); // Obtener el código del aeropuerto
        const dialog = document.getElementById(`myDialog${codigo}`); // Seleccionar el modal correspondiente
        dialog.showModal(); // Mostrar el modal
    });
});

// Obtener todos los botones de cerrar modales
const closeButtons = document.querySelectorAll('.closeDialog');

// Añadir un evento de clic a cada botón de cerrar
closeButtons.forEach(button => {
    button.addEventListener('click', () => {
        const dialog = button.closest('dialog'); // Encontrar el modal más cercano
        dialog.close(); // Cerrar el modal
    });
});