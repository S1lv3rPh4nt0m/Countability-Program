import json
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from fpdf import FPDF

class Transaccion:
    def __init__(self, tipo, descripcion, monto, fecha):
        self.tipo = tipo
        self.descripcion = descripcion
        self.monto = monto
        self.fecha = fecha

    def a_dict(self):
        return {
            'tipo': self.tipo,
            'descripcion': self.descripcion,
            'monto': self.monto,
            'fecha': self.fecha
        }

    @classmethod
    def de_dict(cls, data):
        return cls(data['tipo'], data['descripcion'], data['monto'], data['fecha'])

class SistemaContabilidad:
    def __init__(self, nombre_archivo='transacciones.json'):
        self.transacciones = []
        self.nombre_archivo = nombre_archivo
        self.cargar_transacciones()

    def agregar_transaccion(self, tipo, descripcion, monto, fecha=None):
        try:
            if fecha is None:
                fecha = datetime.now().strftime("%Y-%m-%d")
            transaccion = Transaccion(tipo, descripcion, monto, fecha)
            self.transacciones.append(transaccion)
            self.guardar_transacciones()
        except Exception as e:
            print(f"Error al agregar transacción: {e}")

    def guardar_transacciones(self):
        with open(self.nombre_archivo, 'w') as archivo:
            json.dump([t.a_dict() for t in self.transacciones], archivo, indent=4)

    def cargar_transacciones(self):
        try:
            with open(self.nombre_archivo, 'r') as archivo:
                datos = json.load(archivo)
                self.transacciones = [Transaccion.de_dict(t) for t in datos]
        except FileNotFoundError:
            self.transacciones = []

    def ver_transacciones(self):
        return self.transacciones

    def generar_reporte(self):
        total_gastos = 0
        total_ingresos = 0

        for transaccion in self.transacciones:
            if transaccion.tipo == 'gasto':
                total_gastos += transaccion.monto
            elif transaccion.tipo == 'ingreso':
                total_ingresos += transaccion.monto

        return total_ingresos, total_gastos, total_ingresos - total_gastos

    def generar_reporte_detallado(self, fecha_inicio=None, fecha_fin=None, tipo=None):
        transacciones_filtradas = self.transacciones

        if fecha_inicio:
            transacciones_filtradas = [t for t in transacciones_filtradas if t.fecha >= fecha_inicio]
        if fecha_fin:
            transacciones_filtradas = [t for t in transacciones_filtradas if t.fecha <= fecha_fin]
        if tipo:
            transacciones_filtradas = [t for t in transacciones_filtradas if t.tipo == tipo]

        total_gastos = sum(t.monto for t in transacciones_filtradas if t.tipo == 'gasto')
        total_ingresos = sum(t.monto for t in transacciones_filtradas if t.tipo == 'ingreso')

        return transacciones_filtradas, total_ingresos, total_gastos, total_ingresos - total_gastos

class StylishInputDialog:
    def __init__(self, root, title, prompt):
        self.root = root
        self.title = title
        self.prompt = prompt
        self.result = None
        self.create_dialog()

    def create_dialog(self):
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title(self.title)
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg='#f5f5f5')

        label = tk.Label(self.dialog, text=self.prompt, font=("Segoe UI", 12), bg='#f5f5f5', wraplength=350, justify='left')
        label.pack(pady=10, padx=10, anchor='w')

        self.entry = tk.Entry(self.dialog, font=("Segoe UI", 12), width=50)
        self.entry.pack(pady=5, padx=10)

        button_frame = tk.Frame(self.dialog, bg='#f5f5f5')
        button_frame.pack(pady=10)

        ok_button = tk.Button(button_frame, text="OK", command=self.ok_clicked, font=("Segoe UI", 12), bg='#007BFF', fg='#ffffff')
        ok_button.pack(side=tk.LEFT, padx=5)

        cancel_button = tk.Button(button_frame, text="Cancel", command=self.cancel_clicked, font=("Segoe UI", 12), bg='#FF4D4D', fg='#ffffff')
        cancel_button.pack(side=tk.RIGHT, padx=5)

        self.dialog.grab_set()
        self.root.wait_window(self.dialog)

    def ok_clicked(self):
        self.result = self.entry.get().strip()
        self.dialog.destroy()

    def cancel_clicked(self):
        self.result = None
        self.dialog.destroy()

def mostrar_dialogo(root, title, prompt):
    dialog = StylishInputDialog(root, title, prompt)
    return dialog.result

class AplicacionContabilidad:
    def __init__(self, root):
        self.root = root
        self.sistema = SistemaContabilidad()

        self.root.title("Sistema de Contabilidad")
        self.root.geometry("800x600")
        self.root.configure(bg='#f5f5f5')

        self.frame = tk.Frame(root, bg='#ffffff', padx=20, pady=20, relief=tk.FLAT)
        self.frame.pack(expand=True, fill=tk.BOTH)

        self.label = tk.Label(self.frame, text="Sistema de Contabilidad", font=("Segoe UI", 24, "bold"), bg='#ffffff', fg='#333333')
        self.label.pack(pady=20)

        button_style = {
            'font': ("Segoe UI", 14),
            'bg': '#007BFF',
            'fg': '#ffffff',
            'relief': tk.RAISED,
            'bd': 2,
            'height': 2
        }

        self.boton_agregar = tk.Button(self.frame, text="Agregar Transacción", command=self.agregar_transaccion, **button_style)
        self.boton_agregar.pack(fill=tk.X, pady=10)

        self.boton_ver = tk.Button(self.frame, text="Ver Transacciones", command=self.ver_transacciones, **button_style)
        self.boton_ver.pack(fill=tk.X, pady=10)

        self.boton_reporte = tk.Button(self.frame, text="Generar Reporte", command=self.generar_reporte, **button_style)
        self.boton_reporte.pack(fill=tk.X, pady=10)

        self.boton_reporte_detallado = tk.Button(self.frame, text="Generar Reporte Detallado", command=self.generar_reporte_detallado, **button_style)
        self.boton_reporte_detallado.pack(fill=tk.X, pady=10)

    def agregar_transaccion(self):
        while True:
            tipo = mostrar_dialogo(self.root, "Tipo de Transacción", "Ingrese el tipo de transacción (gasto/ingreso):")
            if tipo is None:
                return
            tipo = tipo.strip().lower()

            if tipo not in ['gasto', 'ingreso']:
                messagebox.showerror("Error", "Tipo de transacción inválido. Intente nuevamente.")
                continue

            descripcion = mostrar_dialogo(self.root, "Descripción", "Ingrese la descripción:")
            if descripcion is None:
                return
            descripcion = descripcion.strip()

            while True:
                monto_str = mostrar_dialogo(self.root, "Monto", "Ingrese el monto:")
                if monto_str is None:
                    return
                try:
                    monto = float(monto_str)
                    if monto < 0:
                        raise ValueError("El monto no puede ser negativo.")
                    break
                except ValueError:
                    messagebox.showerror("Error", "Monto inválido. Ingrese un número válido.")

            fecha = mostrar_dialogo(self.root, "Fecha", "Ingrese la fecha (YYYY-MM-DD) o deje en blanco para hoy:")
            if fecha is None:
                return
            fecha = fecha.strip()
            if fecha == "":
                fecha = None

            self.sistema.agregar_transaccion(tipo, descripcion, monto, fecha)
            messagebox.showinfo("Éxito", "¡Transacción agregada exitosamente!")
            break

    def ver_transacciones(self):
        transacciones = self.sistema.ver_transacciones()

        ventana_transacciones = tk.Toplevel(self.root)
        ventana_transacciones.title("Transacciones")
        ventana_transacciones.geometry("800x500")

        tree = ttk.Treeview(ventana_transacciones, columns=("Fecha", "Tipo", "Descripción", "Monto"), show='headings', height=20)
        tree.heading("Fecha", text="Fecha")
        tree.heading("Tipo", text="Tipo")
        tree.heading("Descripción", text="Descripción")
        tree.heading("Monto", text="Monto")

        # Add Scrollbars Helbert
        vsb = ttk.Scrollbar(ventana_transacciones, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(ventana_transacciones, orient="horizontal", command=tree.xview)
        hsb.pack(side='bottom', fill='x')
        tree.configure(xscrollcommand=hsb.set)

        tree.pack(expand=True, fill=tk.BOTH)

        # Customizing treeview font and colors Helbert
        tree.tag_configure("highlight", font=("Segoe UI", 12, "bold"), foreground="blue")

        for transaccion in transacciones:
            tree.insert("", tk.END, values=(transaccion.fecha, transaccion.tipo, transaccion.descripcion, f"${transaccion.monto:,.2f}"), tags=("highlight",))

    def generar_reporte(self):
        total_ingresos, total_gastos, ganancia_neta = self.sistema.generar_reporte()

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Reporte de Contabilidad', ln=True, align='C')
        pdf.ln(10)
        pdf.set_font('Arial', '', 14)
        pdf.cell(0, 10, f'Total de Ingresos: ${total_ingresos:,.2f}', ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, f'Total de Gastos: ${total_gastos:,.2f}', ln=True)
        pdf.ln(5)
        pdf.cell(0, 10, f'Ganancia Neta: ${ganancia_neta:,.2f}', ln=True)

        pdf.output('reporte.pdf')
        messagebox.showinfo("Reporte", "El reporte ha sido generado en 'reporte.pdf'")

    def generar_reporte_detallado(self):
        fecha_inicio = mostrar_dialogo(self.root, "Fecha de Inicio", "Ingrese la fecha de inicio (YYYY-MM-DD) o deje en blanco:")
        if fecha_inicio is None:
            return
        fecha_inicio = fecha_inicio.strip()

        fecha_fin = mostrar_dialogo(self.root, "Fecha de Fin", "Ingrese la fecha de fin (YYYY-MM-DD) o deje en blanco:")
        if fecha_fin is None:
            return
        fecha_fin = fecha_fin.strip()

        tipo = mostrar_dialogo(self.root, "Tipo de Transacción", "Ingrese el tipo de transacción (gasto/ingreso) o deje en blanco:")
        if tipo is None:
            return
        tipo = tipo.strip().lower()

        transacciones_filtradas, total_ingresos, total_gastos, ganancia_neta = self.sistema.generar_reporte_detallado(fecha_inicio, fecha_fin, tipo)
        ventana_reporte_detallado = tk.Toplevel(self.root)
        ventana_reporte_detallado.title("Reporte Detallado")
        ventana_reporte_detallado.geometry("800x600")

        tree = ttk.Treeview(ventana_reporte_detallado, columns=("Fecha", "Tipo", "Descripción", "Monto"), show='headings', height=20)
        tree.heading("Fecha", text="Fecha")
        tree.heading("Tipo", text="Tipo")
        tree.heading("Descripción", text="Descripción")
        tree.heading("Monto", text="Monto")

        # Add Scrollbars Helbert
        vsb = ttk.Scrollbar(ventana_reporte_detallado, orient="vertical", command=tree.yview)
        vsb.pack(side='right', fill='y')
        tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(ventana_reporte_detallado, orient="horizontal", command=tree.xview)
        hsb.pack(side='bottom', fill='x')
        tree.configure(xscrollcommand=hsb.set)

        tree.pack(expand=True, fill=tk.BOTH)

        # Customizing treeview font and colors Helbert
        tree.tag_configure("highlight", font=("Segoe UI", 12, "bold"), foreground="blue")

        for transaccion in transacciones_filtradas:
            tree.insert("", tk.END, values=(transaccion.fecha, transaccion.tipo, transaccion.descripcion, f"${transaccion.monto:,.2f}"), tags=("highlight",))

        tk.Label(ventana_reporte_detallado, text=f"Total de Ingresos: ${total_ingresos:,.2f}", font=("Segoe UI", 14, "bold"), bg='#ffffff').pack(pady=5)
        tk.Label(ventana_reporte_detallado, text=f"Total de Gastos: ${total_gastos:,.2f}", font=("Segoe UI", 14, "bold"), bg='#ffffff').pack(pady=5)
        tk.Label(ventana_reporte_detallado, text=f"Ganancia Neta: ${ganancia_neta:,.2f}", font=("Segoe UI", 14, "bold"), bg='#ffffff').pack(pady=5)

def main():
    root = tk.Tk()
    app = AplicacionContabilidad(root)
    root.mainloop()

if __name__ == "__main__":
    main()
