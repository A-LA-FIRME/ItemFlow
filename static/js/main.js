/**
 * ItemFlow - Gestor de Items - Aplicación CRUD
 *
 * Este archivo contiene la lógica principal de la aplicación organizada en clases
 * para una mejor estructura y mantenimiento del código.
 */

// Configuración de toastr para notificaciones
toastr.options = {
    closeButton: true,
    progressBar: true,
    positionClass: "toast-bottom-right",
    timeOut: 3000,
    extendedTimeOut: 1000,
    preventDuplicates: true
};

/**
 * Clase para gestionar la API y las llamadas al servidor
 */
class ApiService {
    constructor() {
        this.baseUrl = 'http://localhost:5000/api';
    }

    /**
     * Obtiene todos los items
     * @returns {Promise} Promesa con los datos
     */
    async getItems() {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/items`,
                type: 'GET'
            });
            return response;
        } catch (error) {
            throw new Error('Error al cargar los items');
        }
    }

    /**
     * Obtiene un item por su ID
     * @param {number} id ID del item
     * @returns {Promise} Promesa con los datos del item
     */
    async getItemById(id) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/items/${id}`,
                type: 'GET'
            });
            return response;
        } catch (error) {
            throw new Error('Error al obtener detalles del item');
        }
    }

    /**
     * Crea un nuevo item
     * @param {object} itemData Datos del item a crear
     * @returns {Promise} Promesa con la respuesta del servidor
     */
    async createItem(itemData) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/items`,
                type: 'POST',
                contentType: 'application/json',
                data: JSON.stringify(itemData)
            });
            return response;
        } catch (xhr) {
            if (xhr.status === 409) {
                throw new Error('Ya existe un item con ese nombre. Los nombres deben ser únicos.');
            } else {
                throw new Error('Error al crear el item: ' + (xhr.responseJSON?.error || 'Error desconocido'));
            }
        }
    }

    /**
     * Actualiza un item existente
     * @param {number} id ID del item a actualizar
     * @param {object} itemData Nuevos datos del item
     * @returns {Promise} Promesa con la respuesta del servidor
     */
    async updateItem(id, itemData) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/items/${id}`,
                type: 'PUT',
                contentType: 'application/json',
                data: JSON.stringify(itemData)
            });
            return response;
        } catch (xhr) {
            if (xhr.status === 409) {
                throw new Error('Ya existe otro item con ese nombre. Los nombres deben ser únicos.');
            } else {
                throw new Error('Error al actualizar el item: ' + (xhr.responseJSON?.error || 'Error desconocido'));
            }
        }
    }

    /**
     * Elimina un item
     * @param {number} id ID del item a eliminar
     * @returns {Promise} Promesa con la respuesta del servidor
     */
    async deleteItem(id) {
        try {
            const response = await $.ajax({
                url: `${this.baseUrl}/items/${id}`,
                type: 'DELETE'
            });
            return response;
        } catch (error) {
            throw new Error('Error al eliminar el item');
        }
    }
}

/**
 * Clase para gestionar la interfaz de usuario
 */
class UiManager {
    constructor() {
        this.loadingOverlay = $('#loadingOverlay');

        // Crear el overlay si no existe
        if (this.loadingOverlay.length === 0) {
            $('body').append(`
                <div id="loadingOverlay" class="loading-overlay">
                    <div class="loading-content">
                        <div class="spinner-border text-light" role="status">
                            <span class="visually-hidden">Cargando...</span>
                        </div>
                        <p class="loading-text">Procesando, por favor espere...</p>
                    </div>
                </div>
            `);
            this.loadingOverlay = $('#loadingOverlay');
        }
    }

    showLoading() {
        this.loadingOverlay.addClass('active');
    }

    hideLoading() {
        this.loadingOverlay.removeClass('active');
    }

    /**
     * Muestra una notificación toast
     * @param {string} message Mensaje a mostrar
     * @param {string} type Tipo de notificación (success, error, info, warning)
     */
    showNotification(message, type = 'info') {
        toastr[type](message);
    }

    /**
     * Resetea el formulario de item
     */
    resetForm() {
        $('#itemForm')[0].reset();
        $('#itemId').val('');
        $('#itemPrice').val('0.00');
        $('#itemForm').validate().resetForm();
        $('.is-invalid').removeClass('is-invalid');
    }

    /**
     * Configura el formulario para crear un nuevo item
     */
    setupCreateForm() {
        this.resetForm();
        $('#modalItemLabel').text('Nuevo Item');
        $('#modalItem').modal('show');
    }

    /**
     * Configura el formulario para editar un item existente
     * @param {object} itemData Datos del item a editar
     */
    setupEditForm(itemData) {
        this.resetForm();
        $('#itemId').val(itemData.id);
        $('#itemName').val(itemData.name);
        $('#itemDescription').val(itemData.description);
        $('#itemPrice').val(itemData.price || 0);
        $('#modalItemLabel').text('Editar Item');
        $('#modalItem').modal('show');
    }

    /**
     * Obtiene los datos del formulario
     * @returns {object} Datos del formulario
     */
    getFormData() {
        return {
            name: $('#itemName').val().trim(),
            description: $('#itemDescription').val().trim(),
            price: parseFloat($('#itemPrice').val() || 0)
        };
    }

    /**
     * Muestra el modal de confirmación para eliminar
     */
    showDeleteConfirmation() {
        $('#deleteModal').modal('show');
    }

    /**
     * Oculta el modal de confirmación para eliminar
     */
    hideDeleteConfirmation() {
        $('#deleteModal').modal('hide');
    }

    /**
     * Oculta el modal de item
     */
    hideItemModal() {
        $('#modalItem').modal('hide');
    }
}

/**
 * Clase principal que gestiona la aplicación
 */
class App {
    constructor() {
        this.apiService = new ApiService();
        this.uiManager = new UiManager();
        this.itemsTable = null;
        this.deleteItemId = null;

        this.initValidation();
        this.initDataTable();
        this.bindEvents();
    }

    /**
     * Inicializa la validación del formulario
     */
    initValidation() {
        $('#itemForm').validate({
            rules: {
                itemName: {
                    required: true,
                    minlength: 2,
                    maxlength: 100
                },
                itemPrice: {
                    required: true,
                    number: true,
                    min: 0.01
                }
            },
            messages: {
                itemName: {
                    required: "El nombre es obligatorio",
                    minlength: "El nombre debe tener al menos 2 caracteres",
                    maxlength: "El nombre no puede exceder los 100 caracteres"
                },
                itemPrice: {
                    required: "El precio es obligatorio",
                    number: "Por favor, ingrese un número válido",
                    min: "El precio debe ser mayor a cero"
                }
            },
            errorElement: "div",
            errorClass: "error",
            highlight: function(element) {
                $(element).addClass("is-invalid");
            },
            unhighlight: function(element) {
                $(element).removeClass("is-invalid");
            }
        });
    }

    /**
     * Inicializa la tabla de items con DataTables
     */
    initDataTable() {
        this.uiManager.showLoading();

        this.itemsTable = $('#itemsTable').DataTable({
            ajax: {
                url: `${this.apiService.baseUrl}/items`,
                dataSrc: (json) => json || [],
                error: (xhr, error, thrown) => {
                    this.uiManager.showNotification('Error al cargar datos: ' + thrown, 'error');
                    this.uiManager.hideLoading();
                }
            },
            columns: [
                { data: 'id' },
                { data: 'name' },
                { data: 'description' },
                {
                    data: 'price',
                    render: (data) => {
                        return data !== null && data !== undefined ?
                            '$' + parseFloat(data).toFixed(2) : '$0.00';
                    }
                },
                {
                    data: 'created_at_formatted'},
                {
                    data: null,
                    className: 'action-buttons',
                    orderable: false,
                    render: (data, type, row) => {
                        return `
                            <button class="btn btn-sm btn-outline-primary btn-edit" data-id="${row.id}">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger btn-delete" data-id="${row.id}">
                                <i class="bi bi-trash"></i>
                            </button>
                        `;
                    }
                }
            ],
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json'
            },
            responsive: true,
            pageLength: 10,
            order: [[0, 'desc']],
            initComplete: () => {
                this.uiManager.hideLoading();
            }
        });
    }

    /**
     * Asocia los eventos de la aplicación
     */
    bindEvents() {
        // Evento para el botón "Nuevo Item"
        $('#btnAgregarItem').on('click', () => {
            this.uiManager.setupCreateForm();
        });

        // Evento para guardar item (crear o actualizar)
        $('#itemForm').on('submit', async (e) => {
            e.preventDefault();

            if (!$('#itemForm').valid()) {
                return;
            }

            const itemId = $('#itemId').val();
            const itemData = this.uiManager.getFormData();

            try {
                this.uiManager.showLoading();

                if (itemId) {
                    await this.apiService.updateItem(itemId, itemData);
                    this.uiManager.showNotification('Item actualizado exitosamente', 'success');
                } else {
                    await this.apiService.createItem(itemData);
                    this.uiManager.showNotification('Item creado exitosamente', 'success');
                }

                this.uiManager.hideItemModal();
                this.refreshTable();
            } catch (error) {
                this.uiManager.showNotification(error.message, 'error');
            } finally {
                this.uiManager.hideLoading();
            }
        });

        // Evento para el botón de eliminar en la tabla
        $('#itemsTable').on('click', '.btn-delete', (e) => {
            this.deleteItemId = $(e.currentTarget).data('id');
            this.uiManager.showDeleteConfirmation();
        });

        // Evento para confirmar eliminación
        $('#btnConfirmDelete').on('click', async () => {
            if (this.deleteItemId) {
                try {
                    this.uiManager.showLoading();
                    await this.apiService.deleteItem(this.deleteItemId);
                    this.uiManager.hideDeleteConfirmation();
                    this.refreshTable();
                    this.uiManager.showNotification('Item eliminado exitosamente', 'success');
                } catch (error) {
                    this.uiManager.showNotification(error.message, 'error');
                } finally {
                    this.uiManager.hideLoading();
                }
            }
        });

        // Evento para el botón de editar en la tabla
        $('#itemsTable').on('click', '.btn-edit', async (e) => {
            const itemId = $(e.currentTarget).data('id');

            try {
                this.uiManager.showLoading();
                const itemData = await this.apiService.getItemById(itemId);
                this.uiManager.setupEditForm(itemData);
            } catch (error) {
                this.uiManager.showNotification(error.message, 'error');
            } finally {
                this.uiManager.hideLoading();
            }
        });
    }

    /**
     * Refresca la tabla de items
     */
    refreshTable() {
        this.uiManager.showLoading();
        this.itemsTable.ajax.reload(() => {
            this.uiManager.hideLoading();
        });
    }
}

// Inicialización de la aplicación cuando el documento está listo
$(document).ready(() => {
    const app = new App();
});