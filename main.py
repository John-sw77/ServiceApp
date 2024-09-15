import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect('reparaciones.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS aparatos (
                id INTEGER PRIMARY KEY,
                tipo TEXT,
                marca TEXT,
                modelo TEXT,
                numero_serie TEXT,
                problema TEXT,
                estado TEXT,
                nombre_cliente TEXT,
                telefono_cliente TEXT,
                observaciones TEXT            
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS diagnosticos (
                id INTEGER PRIMARY KEY,
                aparato_id INTEGER,
                diagnostico TEXT,
                valor REAL,
                FOREIGN KEY (aparato_id) REFERENCES aparatos (id)
            )
        ''')
        self.conn.commit()

    def insert_aparato(self, tipo, marca, modelo, numero_serie, problema, estado, nombre_cliente, telefono_cliente):
        self.cursor.execute('''
            INSERT INTO aparatos (tipo, marca, modelo, numero_serie, problema, estado, nombre_cliente, telefono_cliente)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (tipo, marca, modelo, numero_serie, problema, estado, nombre_cliente, telefono_cliente))
        self.conn.commit()
        return self.cursor.lastrowid

    def insert_diagnostico(self, aparato_id, diagnostico, valor):
        self.cursor.execute('''
            INSERT INTO diagnosticos (aparato_id, diagnostico, valor)
            VALUES (?, ?, ?)
        ''', (aparato_id, diagnostico, valor))
        self.conn.commit()

    def get_aparato(self, aparato_id):
        self.cursor.execute('SELECT * FROM aparatos WHERE id = ?', (aparato_id,))
        return self.cursor.fetchone()

    def get_diagnostico(self, aparato_id):
        self.cursor.execute('SELECT * FROM diagnosticos WHERE aparato_id = ?', (aparato_id,))
        return self.cursor.fetchone()

    def update_estado(self, aparato_id, nuevo_estado):
        self.cursor.execute('UPDATE aparatos SET estado = ? WHERE id = ?', (nuevo_estado, aparato_id))
        self.conn.commit()

    def update_observaciones(self, aparato_id, observaciones):
        self.cursor.execute('UPDATE aparatos SET observaciones = ? WHERE id = ?', (observaciones, aparato_id))
        self.conn.commit() 

    def get_all_aparatos(self):
        self.cursor.execute('SELECT id, tipo, marca FROM aparatos')
        return self.cursor.fetchall()       

    def close(self):
        self.conn.close()


class GestionApp(App):
    def build(self):
        self.db = DatabaseManager()
        sm = ScreenManager()
        sm.add_widget(MenuPrincipalScreen(name='menu', db=self.db))
        sm.add_widget(RegistroScreen(name='registro', db=self.db))
        sm.add_widget(DiagnosticoScreen(name='diagnostico', db=self.db))
        sm.add_widget(AprobacionScreen(name='aprobacion', db=self.db))
        sm.add_widget(ReparacionScreen(name='reparacion', db=self.db))
        sm.add_widget(EntregaFacturacionScreen(name='entrega_facturacion', db=self.db))
        return sm
    
    def on_stop(self):
        self.db.close()


class MenuPrincipalScreen(Screen):
    def __init__(self, **kwargs):
        self.db = kwargs.pop('db')
        super().__init__(**kwargs)

        ##layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        ##layout.add_widget(Label(text='Menú Principal'))

        ##self.aparatos_spinner = Spinner(text='Seleccionar aparato')
        ##layout.add_widget(self.aparatos_spinner)
        ##self.actualizar_lista_aparatos()


        # Layout principal
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Logo de la empresa
        logo = Image(source='logo.png', size_hint=(None, None), size=(100, 100))
        logo.pos_hint = {'center_x': 0.5}
        main_layout.add_widget(logo)
        
        main_layout.add_widget(Label(text='Menú Principal', font_size=24, size_hint_y=None, height=50))
        
         # Buscador de aparatos
        search_layout = BoxLayout(size_hint_y=None, height=50)
        self.search_input = TextInput(hint_text='Buscar aparato...', multiline=False)
        search_layout.add_widget(self.search_input)
        search_button = Button(text='Buscar', size_hint_x=None, width=100)
        search_button.bind(on_press=self.search_aparatos)
        search_layout.add_widget(search_button)
        main_layout.add_widget(search_layout)
        
        # Tabla de aparatos
        self.tabla_aparatos = GridLayout(cols=4, spacing=5, size_hint_y=None)
        self.tabla_aparatos.bind(minimum_height=self.tabla_aparatos.setter('height'))
        
        # Encabezados de la tabla
        for header in ['ID', 'Tipo', 'Marca', 'Seleccionar']:
            self.tabla_aparatos.add_widget(Label(text=header, bold=True))
        
        scroll_view = ScrollView(size_hint=(1, None), size=(self.width, 200))
        scroll_view.add_widget(self.tabla_aparatos)
        main_layout.add_widget(scroll_view)
        
        # Botones de navegación
        buttons_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
        buttons_layout.bind(minimum_height=buttons_layout.setter('height'))
        

        buttons = [
            ('Registro', 'registro'),
            ('Diagnóstico', 'diagnostico'),
            ('Aprobación', 'aprobacion'),
            ('Reparación', 'reparacion'),
            ('Entrega y Facturación', 'entrega_facturacion')
        ]
        
    ##    for text, screen in buttons:
    ##        button = Button(text=text)
    ##        button.bind(on_press=lambda x, s=screen: self.change_screen(s))
    ##        layout.add_widget(button)
        
    ##    self.add_widget(layout)

    ##def actualizar_lista_aparatos(self):
    ##    aparatos = self.db.get_all_aparatos()
    ##    self.aparatos_spinner.values = [f"{a[0]} - {a[1]} {a[2]}" for a in aparatos]
    ##    self.aparatos_spinner.bind(text=self.on_aparato_selected)

        for text, screen in buttons:
            button = Button(text=text, size_hint_y=None, height=50)
            button.bind(on_press=lambda x, s=screen: self.change_screen(s))
            buttons_layout.add_widget(button)
        
        main_layout.add_widget(buttons_layout)
        
        self.add_widget(main_layout)
        self.actualizar_lista_aparatos()
    
    def actualizar_lista_aparatos(self):
        self.tabla_aparatos.clear_widgets()
        # Añadir encabezados
        for header in ['ID', 'Tipo', 'Marca', 'Seleccionar']:
            self.tabla_aparatos.add_widget(Label(text=header, bold=True))
        
        aparatos = self.db.get_all_aparatos()
        for aparato in aparatos:
            self.tabla_aparatos.add_widget(Label(text=str(aparato[0])))
            self.tabla_aparatos.add_widget(Label(text=aparato[1]))
            self.tabla_aparatos.add_widget(Label(text=aparato[2]))
            btn = Button(text='Seleccionar')
            btn.bind(on_press=lambda x, id=aparato[0]: self.seleccionar_aparato(id))
            self.tabla_aparatos.add_widget(btn)

    def search_aparatos(self, instance):
        busqueda = self.search_input.text.lower()
        self.tabla_aparatos.clear_widgets()
        # Añadir encabezados
        for header in ['ID', 'Tipo', 'Marca', 'Seleccionar']:
            self.tabla_aparatos.add_widget(Label(text=header, bold=True))
        
        aparatos = self.db.get_all_aparatos()
        for aparato in aparatos:
            if busqueda in str(aparato[0]).lower() or busqueda in aparato[1].lower() or busqueda in aparato[2].lower():
                self.tabla_aparatos.add_widget(Label(text=str(aparato[0])))
                self.tabla_aparatos.add_widget(Label(text=aparato[1]))
                self.tabla_aparatos.add_widget(Label(text=aparato[2]))
                btn = Button(text='Seleccionar')
                btn.bind(on_press=lambda x, id=aparato[0]: self.seleccionar_aparato(id))
                self.tabla_aparatos.add_widget(btn)

    def seleccionar_aparato(self, aparato_id):
        for screen_name in ['diagnostico', 'aprobacion', 'reparacion', 'entrega_facturacion']:
            self.manager.get_screen(screen_name).aparato_id.text = str(aparato_id)
        print(f"Aparato {aparato_id} seleccionado")

    def change_screen(self, screen_name):
        self.manager.current = screen_name     


class RegistroScreen(Screen):
    def __init__(self, **kwargs):
        self.db = kwargs.pop('db')  # Base de datos
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Registro de Aparatos'))
        # Aquí añadiremos más widgets para el registro

# Campos para Datos del Aparato
        self.tipo = TextInput(multiline=False, hint_text='Tipo de artículo')
        layout.add_widget(self.tipo)
        self.marca = TextInput(multiline=False, hint_text='Marca')
        layout.add_widget(self.marca)
        self.modelo = TextInput(multiline=False, hint_text='Modelo')
        layout.add_widget(self.modelo)
        self.numero_serie = TextInput(multiline=False, hint_text='Número de serie')
        layout.add_widget(self.numero_serie)
        self.problema = TextInput(multiline=True, hint_text='Descripción del problema')
        layout.add_widget(self.problema)
        self.estado = TextInput(multiline=False, hint_text='Estado de recepción')
        layout.add_widget(self.estado)
        
        # Campos para Datos del Cliente
        self.nombre_cliente = TextInput(multiline=False, hint_text='Nombre del cliente')
        layout.add_widget(self.nombre_cliente)
        self.telefono_cliente = TextInput(multiline=False, hint_text='Teléfono del cliente')
        layout.add_widget(self.telefono_cliente)
        

        # Botones
        layout.add_widget(Button(text='Guardar información', on_press=self.guardar_info))
        layout.add_widget(Button(text='Imprimir Orden', on_press=self.imprimir_orden))
        layout.add_widget(Button(text='Imprimir Etiqueta', on_press=self.imprimir_etiqueta))
        layout.add_widget(Button(text='Ir a Diagnóstico', on_press=self.ir_a_diagnostico))
        layout.add_widget(Button(text='Volver al Menú Principal', on_press=self.volver_menu))
      
        self.add_widget(layout)

    def volver_menu(self, instance):
        self.manager.current = 'menu'    

    def guardar_info(self, instance):
        aparato_id = self.db.insert_aparato(
            self.tipo.text, self.marca.text, self.modelo.text, self.numero_serie.text,
            self.problema.text, self.estado.text, self.nombre_cliente.text, self.telefono_cliente.text
        )
        print(f"Aparato guardado con ID: {aparato_id}")   

    def imprimir_orden(self, instance):
        orden = f"""
        ORDEN DE INGRESO
        ----------------
        ID: {self.db.last_inserted_id}
        Cliente: {self.nombre_cliente.text}
        Teléfono: {self.telefono_cliente.text}
        Aparato: {self.tipo.text} {self.marca.text} {self.modelo.text}
        Problema: {self.problema.text}
        """
        print("Imprimiendo orden de ingreso:")
        print(orden)

    def imprimir_etiqueta(self, instance):
        etiqueta = f"""
        ID: {self.db.last_inserted_id}
        {self.tipo.text} {self.marca.text}
        {self.modelo.text}
        """
        print("Imprimiendo etiqueta:")
        print(etiqueta)

    def ir_a_diagnostico(self, instance):
        self.manager.current = 'diagnostico'

    __init__ 


class DiagnosticoScreen(Screen):
    def __init__(self, **kwargs):
        self.db = kwargs.pop('db')  # Base de datos
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Diagnóstico y Precio'))
        
        # Revisar estas lineas del codigo anterior y borrar 

        # Campos para información básica del aparato
        ##layout.add_widget(Label(text='Información del aparato:'))
        ##self.info_aparato = TextInput(multiline=True, readonly=True)
        ##layout.add_widget(self.info_aparato)
        
        # Campo para el diagnóstico
        ##layout.add_widget(Label(text='Diagnóstico:'))
        ##self.diagnostico = TextInput(multiline=True)
        ##layout.add_widget(self.diagnostico)
        
        # Campo para el valor de la reparación
        ##layout.add_widget(Label(text='Valor de la reparación:'))
        ##self.valor = TextInput(multiline=False)
        ##layout.add_widget(self.valor)


        # Campos para buscar aparat

        self.aparato_id = TextInput(multiline=False, hint_text='ID del aparato')
        layout.add_widget(self.aparato_id)
        layout.add_widget(Button(text='Buscar aparato', on_press=self.buscar_aparato))
        
        # Campos para información básica del aparato

        self.info_aparato = TextInput(multiline=True, readonly=True)
        layout.add_widget(self.info_aparato)
        
        # Campo para el diagnóstico

        self.diagnostico = TextInput(multiline=True, hint_text='Diagnóstico')
        layout.add_widget(self.diagnostico)
        
        # Campo para el valor de la reparación

        self.valor = TextInput(multiline=False, hint_text='Valor de la reparación')
        layout.add_widget(self.valor)
        
        # Botón para guardar
        layout.add_widget(Button(text='Guardar diagnóstico y precio', on_press=self.guardar_diagnostico))
        layout.add_widget(Button(text='Ir a Aprobación', on_press=self.ir_a_aprobacion))
        layout.add_widget(Button(text='Volver al Registro', on_press=self.volver_a_registro))
        layout.add_widget(Button(text='Volver al Menú Principal', on_press=self.volver_menu))
        
        self.add_widget(layout)

    def volver_menu(self, instance):
        self.manager.current = 'menu'    

    def buscar_aparato(self, instance):
        aparato_id = int(self.aparato_id.text)
        aparato = self.db.get_aparato(aparato_id)
        if aparato:
            self.info_aparato.text = f"Tipo: {aparato[1]}\nMarca: {aparato[2]}\nModelo: {aparato[3]}\nProblema: {aparato[5]}"
        else:
            self.info_aparato.text = "Aparato no encontrado"

        # Metodo del boton anterior
    #def guardar_diagnostico(self, instance):
        # Aquí iría la lógica para guardar el diagnóstico y precio
        #print("Diagnóstico guardado")    

    def guardar_diagnostico(self, instance):
        aparato_id = int(self.aparato_id.text)
        self.db.insert_diagnostico(aparato_id, self.diagnostico.text, float(self.valor.text))
        print("Diagnóstico guardado")            

    def volver_a_registro(self, instance):
        self.manager.current = 'registro'

    def ir_a_aprobacion(self, instance):
        self.manager.current = 'aprobacion'
 

    __init__     


class AprobacionScreen(Screen):
    def __init__(self, **kwargs):
        self.db = kwargs.pop('db')  # Base de datos
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Aprobación del Cliente'))
        
        # Revisar estas lineas del codigo anterior y borrar 

        # Campo de búsqueda
        #layout.add_widget(Label(text='Buscar aparato:'))
        #self.busqueda = TextInput(multiline=False)
        #layout.add_widget(self.busqueda)
        
        # Botón de búsqueda
        #layout.add_widget(Button(text='Buscar', on_press=self.buscar_aparato))
        
        # Información del aparato
        #self.info_aparato = TextInput(multiline=True, readonly=True)
        #layout.add_widget(self.info_aparato)
        
        # Estado actual
        #layout.add_widget(Label(text='Estado actual:'))
        #self.estado = Spinner(text='Seleccionar', values=('Revisado', 'Aprobado', 'En reparación'))
        #layout.add_widget(self.estado)

        # Campo y Botón de búsqueda

        self.aparato_id = TextInput(multiline=False, hint_text='ID del aparato')
        layout.add_widget(self.aparato_id)
        layout.add_widget(Button(text='Buscar', on_press=self.buscar_aparato))
        
        # Información del aparato

        self.info_aparato = TextInput(multiline=True, readonly=True)
        layout.add_widget(self.info_aparato)
        
        # Estado actual

        self.estado = Spinner(text='Seleccionar', values=('Revisado', 'Aprobado', 'En reparación'))
        layout.add_widget(self.estado)


        
        # Botón de aprobación
        layout.add_widget(Button(text='Aprobar', on_press=self.aprobar))
        
        # ir a la pantalla de Estado de Reparación :)
        layout.add_widget(Button(text='Ir a Estado de Reparación', on_press=self.ir_a_estado_reparacion))

        # Botón para volver
        layout.add_widget(Button(text='Volver al Diagnóstico', on_press=self.volver_a_diagnostico))
        
        layout.add_widget(Button(text='Volver al Menú Principal', on_press=self.volver_menu))

        self.add_widget(layout)
    
    ##def buscar_aparato(self, instance):
        # Aquí iría la lógica para buscar el aparato
    ##    print("Buscando aparato...")
    
    ##def aprobar(self, instance):
        # Aquí iría la lógica para aprobar la reparación
    ##    print("Aprobación guardada")

    def volver_menu(self, instance):
        self.manager.current = 'menu'

    def buscar_aparato(self, instance):
        aparato_id = int(self.aparato_id.text)
        aparato = self.db.get_aparato(aparato_id)
        diagnostico = self.db.get_diagnostico(aparato_id)
        if aparato and diagnostico:
            self.info_aparato.text = f"Tipo: {aparato[1]}\nMarca: {aparato[2]}\nModelo: {aparato[3]}\nDiagnóstico: {diagnostico[2]}\nValor: {diagnostico[3]}"
        else:
            self.info_aparato.text = "Información no encontrada"

    def aprobar(self, instance):
        aparato_id = int(self.aparato_id.text)
        self.db.update_estado(aparato_id, self.estado.text)
        print("Estado actualizado")

    def ir_a_estado_reparacion(self, instance):
        self.manager.current = 'estado_reparacion'
    
    def volver_a_diagnostico(self, instance):
        self.manager.current = 'diagnostico'

    __init__    


class ReparacionScreen(Screen):
    def __init__(self, **kwargs):
        self.db = kwargs.pop('db')   # Base de datos
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Estado de Reparación'))
        
        # Información básica del aparato
        ##layout.add_widget(Label(text='Información del aparato:'))
        ##self.info_aparato = TextInput(multiline=True, readonly=True)
        ##layout.add_widget(self.info_aparato)
        
        # Diagnóstico
        ##layout.add_widget(Label(text='Diagnóstico:'))
        ##self.diagnostico = TextInput(multiline=True, readonly=True)
        ##layout.add_widget(self.diagnostico)
        
        # Valor de la reparación
        ##layout.add_widget(Label(text='Valor de la reparación:'))
        ##self.valor = TextInput(multiline=False, readonly=True)
        ##layout.add_widget(self.valor)
        
        # Observaciones finales
        ##layout.add_widget(Label(text='Observaciones finales:'))
        ##self.observaciones = TextInput(multiline=True)
        ##layout.add_widget(self.observaciones)

        self.aparato_id = TextInput(multiline=False, hint_text='ID del aparato')
        layout.add_widget(self.aparato_id)
        layout.add_widget(Button(text='Buscar', on_press=self.buscar_aparato))
        
        self.info_aparato = TextInput(multiline=True, readonly=True)
        layout.add_widget(self.info_aparato)
        
        self.observaciones = TextInput(multiline=True, hint_text='Observaciones finales')
        layout.add_widget(self.observaciones)
        
        # Botón para marcar como listo
        layout.add_widget(Button(text='Marcar como Listo', on_press=self.marcar_listo))
        
        layout.add_widget(Button(text='Ir a Entrega y Facturación', on_press=self.ir_a_entrega_facturacion))
    
        layout.add_widget(Button(text='Volver a Aprobación', on_press=self.volver_a_aprobacion))
        
        layout.add_widget(Button(text='Volver al Menú Principal', on_press=self.volver_menu))

        self.add_widget(layout)

    def buscar_aparato(self, instance):
        aparato_id = int(self.aparato_id.text)
        aparato = self.db.get_aparato(aparato_id)
        diagnostico = self.db.get_diagnostico(aparato_id)
        if aparato and diagnostico:
            self.info_aparato.text = f"Tipo: {aparato[1]}\nMarca: {aparato[2]}\nModelo: {aparato[3]}\nEstado: {aparato[6]}\nDiagnóstico: {diagnostico[2]}\nValor: {diagnostico[3]}"
        else:
            self.info_aparato.text = "Información no encontrada"

    def marcar_listo(self, instance):
        # Aquí iría la lógica para marcar el aparato como listo
        aparato_id = int(self.aparato_id.text)
        self.db.update_estado(aparato_id, "Listo")
        print("Aparato marcado como listo")            

    def ir_a_entrega_facturacion(self, instance):
        self.manager.current = 'entrega_facturacion'    
    
    def volver_a_aprobacion(self, instance):
        self.manager.current = 'aprobacion'

    def volver_menu(self, instance):
        self.manager.current = 'menu'

    __init__    


class EntregaFacturacionScreen(Screen):
    def __init__(self, **kwargs):
        self.db = kwargs.pop('db')   # Base de datos
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        layout.add_widget(Label(text='Entrega y Facturación'))
        
        # Creamos un GridLayout para organizar la información
        ##grid = GridLayout(cols=2, spacing=10)
        
        # Información básica del aparato
        ##grid.add_widget(Label(text='Información del aparato:'))
        ##self.info_aparato = TextInput(multiline=True, readonly=True)
        ##grid.add_widget(self.info_aparato)
        
        # Datos del cliente
        ##grid.add_widget(Label(text='Datos del cliente:'))
        ##self.datos_cliente = TextInput(multiline=True, readonly=True)
        ##grid.add_widget(self.datos_cliente)
        
        # Diagnóstico
        ##grid.add_widget(Label(text='Diagnóstico:'))
        ##self.diagnostico = TextInput(multiline=True, readonly=True)
        ##grid.add_widget(self.diagnostico)
        
        # Observaciones de la reparación
        ##grid.add_widget(Label(text='Observaciones:'))
        ##self.observaciones = TextInput(multiline=True, readonly=True)
        ##grid.add_widget(self.observaciones)
        
        # Valor
        ##grid.add_widget(Label(text='Valor:'))
        ##self.valor = TextInput(readonly=True)
        ##grid.add_widget(self.valor)
        
        ##layout.add_widget(grid)

        self.aparato_id = TextInput(multiline=False, hint_text='ID del aparato')
        layout.add_widget(self.aparato_id)
        layout.add_widget(Button(text='Buscar', on_press=self.buscar_aparato))
        
        self.info_aparato = TextInput(multiline=True, readonly=True)
        layout.add_widget(self.info_aparato)
        
        # Botones
        layout.add_widget(Button(text='Facturar', on_press=self.facturar))
        layout.add_widget(Button(text='Imprimir factura', on_press=self.imprimir_factura))
        layout.add_widget(Button(text='Volver a Estado de Reparación', on_press=self.volver_a_estado_reparacion))
        layout.add_widget(Button(text='Volver al Menú Principal', on_press=self.volver_menu))

        self.add_widget(layout)

    def volver_menu(self, instance):
        self.manager.current = 'menu'    

    def buscar_aparato(self, instance):
        aparato_id = int(self.aparato_id.text)
        aparato = self.db.get_aparato(aparato_id)
        diagnostico = self.db.get_diagnostico(aparato_id)
        if aparato and diagnostico:
            self.info_aparato.text = f"Tipo: {aparato[1]}\nMarca: {aparato[2]}\nModelo: {aparato[3]}\nEstado: {aparato[6]}\nCliente: {aparato[7]}\nTeléfono: {aparato[8]}\nDiagnóstico: {diagnostico[2]}\nValor: {diagnostico[3]}"
        else:
            self.info_aparato.text = "Información no encontrada"    
    
    def facturar(self, instance):
        aparato_id = int(self.aparato_id.text)
        aparato = self.db.get_aparato(aparato_id)
        diagnostico = self.db.get_diagnostico(aparato_id)
        if aparato and diagnostico:
            factura = f"""
            FACTURA
            -------
            Cliente: {aparato[7]}
            Teléfono: {aparato[8]}
            Aparato: {aparato[1]} {aparato[2]} {aparato[3]}
            Diagnóstico: {diagnostico[2]}
            Valor: ${diagnostico[3]}
            """
            self.factura_actual = factura
            print("Factura generada")
        else:
            print("No se pudo generar la factura")

    def imprimir_factura(self, instance):
        if hasattr(self, 'factura_actual'):
            # En un entorno real, aquí enviarías la factura a una impresora
            print("Imprimiendo factura:")
            print(self.factura_actual)
        else:
            print("No hay factura para imprimir")
     
    def volver_a_estado_reparacion(self, instance):
        self.manager.current = 'estado_reparacion'

    __init__    


if __name__ == '__main__':
    GestionApp().run()