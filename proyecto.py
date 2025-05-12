from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QPainterPath
import sys
import math


class Conexion:
    def __init__(self, nodo_a, nodo_b, contenedor, tipo=0):
        """
        Inicializa la conexión entre dos nodos y la registra en el contenedor principal.
        El parámetro 'tipo' determina la representación gráfica:
         - tipo 0: línea recta.
         - tipo 1: curva hacia la derecha.
         - tipo 2: curva hacia la izquierda.
        """
        self.nodo_a = nodo_a
        self.nodo_b = nodo_b
        self.contenedor = contenedor
        self.tipo = tipo  # Tipo de conexión (curva o recta)

        # Añadir la conexión a la lista de conexiones del contenedor principal.
        if hasattr(contenedor, 'conexiones'):
            contenedor.conexiones.append(self)
        else:
            contenedor.conexiones = [self]
        
        # Solicitar redibujado de la ventana.
        contenedor.update()

    def dibujar(self, pintor):
        """
        Dibuja la conexión entre los centros de los dos nodos.
        Según el tipo se dibuja:
         - Una línea recta (tipo == 0)
         - Una curva cuadrática (tipo 1 o 2):
            -No te asustes al hablar de cuadrática esta inspirado en videojuegos como la caida de una bala :P
        """
        # Calcula los centros de ambos nodos.
        x1 = self.nodo_a.x() + self.nodo_a.width() / 2
        y1 = self.nodo_a.y() + self.nodo_a.height() / 2
        x2 = self.nodo_b.x() + self.nodo_b.width() / 2
        y2 = self.nodo_b.y() + self.nodo_b.height() / 2

        if self.tipo == 0:
            # Dibuja una línea recta para la primera conexión.
            pintor.drawLine(int(x1), int(y1), int(x2), int(y2))
            return

        # Normalizar el orden para mantener la consistencia en la curvatura
        if (x1, y1) > (x2, y2):
            x1, y1, x2, y2 = x2, y2, x1, y1

        # Calcular el punto medio entre ambos nodos.
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx = x2 - x1
        dy = y2 - y1
        distancia = math.hypot(dx, dy)
        if distancia == 0:
            distancia = 1  # Evitar división por cero

        desplazamiento = 20  # Intensidad de la curvatura
        # Determinar dirección de la curva según el tipo
        if self.tipo == 1:
            factor = 1
        elif self.tipo == 2:
            factor = -1
        else:
            pintor.drawLine(int(x1), int(y1), int(x2), int(y2))
            return

        # Calcular el punto de control para la curva cuadrática
        cx = mx + factor * desplazamiento * (dy / distancia)
        cy = my - factor * desplazamiento * (dx / distancia)

        # Dibuja la curva
        ruta = QPainterPath()
        ruta.moveTo(x1, y1)
        ruta.quadTo(cx, cy, x2, y2)
        pintor.drawPath(ruta)

class Nodo(QPushButton):
    # Variable de clase para recordar el nodo actualmente seleccionado.
    nodo_seleccionado = None

    def __init__(self, contenedor, posicion: tuple, etiqueta: str):
        super().__init__(contenedor)
        self.etiqueta = etiqueta
        self.posicion = posicion
        # Diccionario para almacenar conexiones a otros nodos (soporta múltiples conexiones)
        self.nodos_relacionados = {}
        self.setText(self.etiqueta)
        self.setStyleSheet("""
            color: white;
            background-color: rgba(100,100,100,0.7);
            border-radius: 10px;
            width: 20px;
            height: 20px;
        """)
        self.ajustar_posicion()

    def ajustar_posicion(self):
        x, y = self.posicion
        self.setGeometry(x, y, 25, 25)

    def mousePressEvent(self, evento):
        if evento.button() == Qt.LeftButton:
            if Nodo.nodo_seleccionado is None:
                # Selecciona el nodo actual.
                Nodo.nodo_seleccionado = self
                self.setStyleSheet("""
                    color: white;
                    background-color: rgba(50,50,50,0.7);
                    border-radius: 10px;
                    width: 20px;
                    height: 20px;
                """)
            else:
                if Nodo.nodo_seleccionado == self:
                    # Si el mismo nodo es seleccionado, cancelar selección.
                    self.setStyleSheet("""
                        color: white;
                        background-color: rgba(100,100,100,0.7);
                        border-radius: 10px;
                        width: 20px;
                        height: 20px;
                    """)
                    Nodo.nodo_seleccionado = None
                else:
                    contenedor = self.parent()
                    # Contar cuántas conexiones ya existen entre estos dos nodos.
                    cantidad = 0
                    for conexion in contenedor.conexiones:
                        if ((conexion.nodo_a == Nodo.nodo_seleccionado and conexion.nodo_b == self) or 
                            (conexion.nodo_b == Nodo.nodo_seleccionado and conexion.nodo_a == self)):
                            cantidad += 1

                    if cantidad >= 3:
                        print("Ya existen 3 conexiones entre estos nodos.")
                        Nodo.nodo_seleccionado.setStyleSheet("""
                            color: white;
                            background-color: rgba(100,100,100,0.7);
                            border-radius: 10px;
                            width: 20px;
                            height: 20px;
                        """)
                        Nodo.nodo_seleccionado = None
                        return

                    # Crear la conexión usando la cantidad como tipo para definir la curva
                    conexion = Conexion(Nodo.nodo_seleccionado, self, contenedor, tipo=cantidad)
                    # Registrar la conexión en ambos nodos
                    Nodo.nodo_seleccionado.agregar_conexion(self.etiqueta, self, conexion)
                    self.agregar_conexion(Nodo.nodo_seleccionado.etiqueta, Nodo.nodo_seleccionado, conexion)
                    Nodo.nodo_seleccionado.setStyleSheet("""
                        color: white;
                        background-color: rgba(100,100,100,0.7);
                        border-radius: 10px;
                        width: 20px;
                        height: 20px;
                    """)
                    Nodo.nodo_seleccionado = None

        elif evento.button() == Qt.RightButton:
            # Elimina el nodo y todas sus conexiones con clic derecho.
            if Nodo.nodo_seleccionado == self:
                Nodo.nodo_seleccionado = None
            self.eliminar_nodo()

        super().mousePressEvent(evento)

    def eliminar_nodo(self):
        # Elimina todas las conexiones de este nodo con otros.
        for etiqueta_relacionada, conexiones in list(self.nodos_relacionados.items()):
            for nodo, conexion in conexiones:
                nodo.remover_conexion(self.etiqueta)
                if conexion is not None and hasattr(self.parent(), "conexiones"):
                    if conexion in self.parent().conexiones:
                        self.parent().conexiones.remove(conexion)
                        self.parent().update()
        print(f"Nodo {self.etiqueta} eliminado.")
        self.deleteLater()

    def agregar_conexion(self, etiqueta, nodo, conexion=None):
        # Permite agregar hasta 3 conexiones entre dos nodos.
        if etiqueta in self.nodos_relacionados:
            if len(self.nodos_relacionados[etiqueta]) < 3:
                self.nodos_relacionados[etiqueta].append([nodo, conexion])
            else:
                print(f"Máximo de conexiones alcanzado entre {self.etiqueta} y {nodo.etiqueta}.")
                return
        else:
            self.nodos_relacionados[etiqueta] = [[nodo, conexion]]
        print(f"Conexión creada entre {self.etiqueta} y {nodo.etiqueta}.")

    def remover_conexion(self, etiqueta):
        try:
            del self.nodos_relacionados[etiqueta]
            print(f"Conexión eliminada entre {self.etiqueta} y {etiqueta}.")
        except KeyError:
            print(f"No existía conexión entre {self.etiqueta} y {etiqueta}.")

class Interfaz(QWidget):
    def __init__(self):
        super().__init__()
        self.conexiones = []  # Lista de todas las conexiones.
        self.siguiente_letra = ord("E")  # Para asignar nombres a nuevos nodos.
        self.inicializar_interfaz()

    def inicializar_interfaz(self):
        self.setGeometry(100, 100, 600, 400)
        self.setWindowTitle("Conexión de Nodos")
        # Crear algunos nodos de ejemplo.
        self.nodo1 = Nodo(self, (50, 50), "A")
        self.nodo2 = Nodo(self, (200, 50), "B")
        self.nodo3 = Nodo(self, (350, 150), "C")
        self.nodo4 = Nodo(self, (100, 300), "D")
        
        # Botón para detectar ciclos.
        self.boton_ciclos = QPushButton("Detectar ciclos", self)
        self.boton_ciclos.setGeometry(480, 10, 110, 30)
        self.boton_ciclos.clicked.connect(self.buscar_ciclos)
        
        self.show()
        # Mensaje de bienvenida y breve tutorial.
        QMessageBox.information(self, 'Información', """Proyecto desarrollado por:
                                \n Israel Monteagut Santiesteban
                                \n • Haz clic en un área vacía para crear un nuevo nodo
                                \n • Haz clic en un nodo y luego en otro para enlazarlos
                                \n • Haz clic derecho sobre un nodo para eliminarlo
                                \n ¡Gracias por usar la aplicación! ❤️""")

    def mousePressEvent(self, evento):
        """
        Permite crear un nuevo nodo si se hace clic en un área vacía.
        El nodo se centra en la posición del clic.
        """
        if evento.button() == Qt.LeftButton:
            if self.childAt(evento.pos()) is None:
                x = evento.pos().x() - 25
                y = evento.pos().y() - 25
                etiqueta = chr(self.siguiente_letra)
                self.siguiente_letra += 1
                nuevo_nodo = Nodo(self, (x, y), etiqueta)
                nuevo_nodo.show()
        super().mousePressEvent(evento)

    def paintEvent(self, _):
        """
        Dibuja todas las conexiones existentes sobre la interfaz.
        """
        pintor = QPainter(self)
        lapiz = QPen(Qt.black, 2)
        pintor.setPen(lapiz)
        for conexion in self.conexiones:
            conexion.dibujar(pintor)
    
    def buscar_ciclos(self):
        """
        Construye el grafo a partir de los nodos y sus conexiones y detecta:
            - ciclos simples de 3 o más nodos mediante DFS (Depth-First Search o Búsqueda en Profundidad) :P
            - ciclos de longitud 2 si existen múltiples conexiones entre dos nodos
        Muestra los ciclos encontrados en un cuadro de diálogo.
        """
        nodos = self.findChildren(Nodo)
        
        # Representar el grafo como un diccionario {etiqueta: set(vecinos)}
        grafo = {}
        for nodo in nodos:
            grafo[nodo.etiqueta] = set()
            for conexiones in nodo.nodos_relacionados.values():
                for (vecino, _) in conexiones:
                    grafo[nodo.etiqueta].add(vecino.etiqueta)
        
        ciclos_dfs = set()   # ciclos de 3 o más nodos
        ciclos_dobles = set() # ciclos de 2 nodos por múltiples conexiones

        # Buscar ciclos de longitud 2 o autoenlaces
        for nodo in nodos:
            for conexiones in nodo.nodos_relacionados.values():
                if len(conexiones) > 1:
                    vecino = conexiones[0][0]
                    if nodo.etiqueta == vecino.etiqueta:
                        ciclos_dobles.add((nodo.etiqueta,))
                    else:
                        if nodo.etiqueta < vecino.etiqueta:
                            ciclos_dobles.add((nodo.etiqueta, vecino.etiqueta))
        
        # DFS para ciclos de 3 o más nodos
        def dfs(actual, inicio, recorrido):
            for vecino in grafo[actual]:
                if vecino == inicio and len(recorrido) >= 3:
                    ciclos_dfs.add(tuple(recorrido))
                elif vecino not in recorrido and vecino > inicio:
                    dfs(vecino, inicio, recorrido + [vecino])
        
        for etiqueta in sorted(grafo.keys()):
            dfs(etiqueta, etiqueta, [etiqueta])
        
        # Unir ambos tipos de ciclos
        ciclos_encontrados = ciclos_dfs.union(ciclos_dobles)
        
        resultado = []
        
        if ciclos_encontrados:
            resultado.append("Ciclos encontrados:")
            for ciclo in ciclos_encontrados:
                if len(ciclo) == 1:
                    resultado.append("Ciclo en el nodo: " + ciclo[0])
                elif len(ciclo) == 2:
                    resultado.append(" -> ".join(ciclo) + " -> " + ciclo[0])
                else:
                    resultado.append(" -> ".join(ciclo) + " -> " + ciclo[0])
        else:
            resultado.append("No se detectaron ciclos.")
        
        texto = "\n".join(resultado)
        QMessageBox.information(self, 'Ciclos', texto)


if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        interfaz = Interfaz()
        sys.exit(app.exec_())
    except Exception as error:
        print(error)
        input("Presione Enter para cerrar.")
