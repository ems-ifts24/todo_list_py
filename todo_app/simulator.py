"""
Módulo de simulación de tareas.
Coordina la generación de datos simulados y la visualización de gráficos.
"""
import json
from pathlib import Path
from typing import Optional
from colorama import Style

from todo_app.services.data_generator import DataGenerator
from todo_app.services.graphics_service import GraphicsService
from todo_app.utils.ui_utils import ConsoleUI, TextColor


class Simulator:
    """Clase que maneja el submenú de simulación."""
    
    def __init__(self):
        """Inicializa el simulador."""
        self.data_generator = DataGenerator()
        self.graphics_service = GraphicsService()
        self.running = True
        self.current_simulated_file: Optional[str] = None
        
        # Opciones del menú de simulación
        self.menu_options = {
            "1": ("📊 Generar N registros simulados", self.generate_simulated_data),
            "2": ("📈 Gráfico: Tareas por Prioridad", self.plot_priority),
            "3": ("📊 Gráfico: Tareas por Estado", self.plot_status),
            "4": ("📉 Gráfico: Distribución Temporal", self.plot_temporal),
            "5": ("🔥 Gráfico: Prioridad vs Estado (heatmap)", self.plot_heatmap),
            "6": ("🥧 Gráfico: Proporción por Prioridad (pie)", self.plot_priority_pie),
            "7": ("🥧 Gráfico: Proporción por Estado (pie)", self.plot_status_pie),
            "8": ("📈 Gráfico: Tendencia de Estados (stackplot)", self.plot_trend),
            "9": ("🎯 Mostrar 4 gráficos juntos", self.plot_multiple),
            "0": ("🔙 Volver al menú principal", self.exit_simulator)
        }
    
    def run(self) -> None:
        """Ejecuta el bucle principal del simulador."""
        # Verificar si existe un archivo simulado previo
        latest_file = self.data_generator.get_latest_simulated_file()
        if latest_file:
            self.current_simulated_file = str(latest_file)
        
        try:
            while self.running:
                self._show_simulator_menu()
                self._handle_menu_selection()
        except KeyboardInterrupt:
            ConsoleUI.print_info("\nSaliendo del simulador...")
            self.running = False
    
    def _show_simulator_menu(self) -> None:
        """Muestra el menú de simulación."""
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("🎲 SIMULADOR DE TAREAS")
        
        # Mostrar estado del archivo simulado
        if self.current_simulated_file:
            ConsoleUI.print_success(f"Archivo simulado activo: {self.current_simulated_file}")
            
            # Mostrar conteo de registros reales y simulados
            real_count, simulated_count = self._count_real_and_simulated_tasks()
            print(f"{TextColor.INFO.value}Reg. reales = {real_count}  |  Registros simulados = {simulated_count}{Style.RESET_ALL}")
        else:
            ConsoleUI.print_warning("No hay archivo simulado. Genere uno primero (opción 1).")
        
        print()
        
        # Mostrar opciones del menú
        for key, (label, _) in self.menu_options.items():
            print(f"{TextColor.INFO.value}{key}.{Style.RESET_ALL} {label}")
    
    def _count_real_and_simulated_tasks(self) -> tuple[int, int]:
        """Cuenta los registros reales y simulados.
        
        Returns:
            Tupla con (cantidad de registros reales, cantidad de registros simulados)
        """
        real_count = 0
        simulated_count = 0
        
        # Contar registros reales
        real_file = Path("data") / "tareas.json"
        if real_file.exists():
            try:
                with open(real_file, 'r', encoding='utf-8') as f:
                    real_tasks = json.load(f)
                    real_count = len(real_tasks)
            except (json.JSONDecodeError, FileNotFoundError):
                real_count = 0
        
        # Contar registros en el archivo simulado
        if self.current_simulated_file:
            try:
                with open(self.current_simulated_file, 'r', encoding='utf-8') as f:
                    all_tasks = json.load(f)
                    total_count = len(all_tasks)
                    # Los simulados son el total menos los reales
                    simulated_count = total_count - real_count
            except (json.JSONDecodeError, FileNotFoundError):
                simulated_count = 0
        
        return real_count, simulated_count
    
    def _handle_menu_selection(self) -> None:
        """Maneja la selección del usuario."""
        choice = input("\nSeleccione una opción: ").strip()
        
        if choice in self.menu_options:
            _, action = self.menu_options[choice]
            action()
        else:
            ConsoleUI.print_error("Opción inválida. Por favor, intente de nuevo.")
            input("\nPresione Enter para continuar...")
    
    def generate_simulated_data(self) -> None:
        """Genera N registros simulados."""
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("📊 GENERAR REGISTROS SIMULADOS")
        
        # Solicitar cantidad de registros
        while True:
            count_input = ConsoleUI.input_with_prompt(
                "Cantidad de registros a generar (default: 100)",
                "100"
            )
            
            # Si no ingresa nada o solo espacios, usar el valor por defecto
            if not count_input or not count_input.strip():
                count_input = "100"
            
            try:
                count = int(count_input.strip())
                if count <= 0:
                    ConsoleUI.print_error("La cantidad debe ser mayor a 0.")
                    continue
                if count > 10000:
                    ConsoleUI.print_warning("Generar más de 10,000 registros puede tardar.")
                    if not ConsoleUI.confirm("¿Desea continuar?", False):
                        input("\nPresione Enter para continuar...")
                        return
                break
            except ValueError:
                ConsoleUI.print_error("Ingrese un número válido.")
        
        # Generar datos
        try:
            ConsoleUI.print_info(f"Generando {count} registros simulados...")
            file_path = self.data_generator.generate_simulated_tasks(count)
            self.current_simulated_file = file_path
            
            ConsoleUI.print_success(f"✅ Se generaron {count} registros exitosamente.")
            ConsoleUI.print_info(f"Archivo guardado en: {file_path}")
            
        except Exception as e:
            ConsoleUI.print_error(f"Error al generar registros: {str(e)}")
        
        input("\nPresione Enter para continuar...")
    
    def _check_simulated_file(self) -> bool:
        """Verifica que exista un archivo simulado.
        
        Returns:
            True si existe, False en caso contrario
        """
        if not self.current_simulated_file:
            ConsoleUI.print_warning("No hay archivo simulado disponible.")
            ConsoleUI.print_info("Genere registros simulados primero (opción 1).")
            input("\nPresione Enter para continuar...")
            return False
        return True
    
    def plot_priority(self) -> None:
        """Genera gráfico de tareas por prioridad."""
        if not self._check_simulated_file():
            return
        
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("📈 GRÁFICO: TAREAS POR PRIORIDAD")
        
        try:
            ConsoleUI.print_info("Generando gráfico...")
            self.graphics_service.plot_tasks_by_priority(self.current_simulated_file)
        except Exception as e:
            ConsoleUI.print_error(f"Error al generar gráfico: {str(e)}")
            input("\nPresione Enter para continuar...")
    
    def plot_status(self) -> None:
        """Genera gráfico de tareas por estado."""
        if not self._check_simulated_file():
            return
        
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("📊 GRÁFICO: TAREAS POR ESTADO")
        
        try:
            ConsoleUI.print_info("Generando gráfico...")
            self.graphics_service.plot_tasks_by_status(self.current_simulated_file)
        except Exception as e:
            ConsoleUI.print_error(f"Error al generar gráfico: {str(e)}")
            input("\nPresione Enter para continuar...")
    
    def plot_temporal(self) -> None:
        """Genera gráfico de distribución temporal."""
        if not self._check_simulated_file():
            return
        
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("📉 GRÁFICO: DISTRIBUCIÓN TEMPORAL")
        
        try:
            ConsoleUI.print_info("Generando gráfico...")
            self.graphics_service.plot_temporal_distribution(self.current_simulated_file)
        except Exception as e:
            ConsoleUI.print_error(f"Error al generar gráfico: {str(e)}")
            input("\nPresione Enter para continuar...")
    
    def plot_heatmap(self) -> None:
        """Genera heatmap de prioridad vs estado."""
        if not self._check_simulated_file():
            return
        
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("🔥 GRÁFICO: PRIORIDAD VS ESTADO (HEATMAP)")
        
        try:
            ConsoleUI.print_info("Generando gráfico...")
            self.graphics_service.plot_priority_vs_status_heatmap(self.current_simulated_file)
        except Exception as e:
            ConsoleUI.print_error(f"Error al generar gráfico: {str(e)}")
            input("\nPresione Enter para continuar...")
    
    def plot_priority_pie(self) -> None:
        """Genera gráfico de torta por prioridad."""
        if not self._check_simulated_file():
            return
        
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("🥧 GRÁFICO: PROPORCIÓN POR PRIORIDAD (PIE)")
        
        try:
            ConsoleUI.print_info("Generando gráfico...")
            self.graphics_service.plot_priority_pie_chart(self.current_simulated_file)
        except Exception as e:
            ConsoleUI.print_error(f"Error al generar gráfico: {str(e)}")
            input("\nPresione Enter para continuar...")
    
    def plot_status_pie(self) -> None:
        """Genera gráfico de torta por estado."""
        if not self._check_simulated_file():
            return
        
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("🥧 GRÁFICO: PROPORCIÓN POR ESTADO (PIE)")
        
        try:
            ConsoleUI.print_info("Generando gráfico...")
            self.graphics_service.plot_status_pie_chart(self.current_simulated_file)
        except Exception as e:
            ConsoleUI.print_error(f"Error al generar gráfico: {str(e)}")
            input("\nPresione Enter para continuar...")
    
    def plot_trend(self) -> None:
        """Genera gráfico de tendencia de estados."""
        if not self._check_simulated_file():
            return
        
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("📈 GRÁFICO: TENDENCIA DE ESTADOS (STACKPLOT)")
        
        try:
            ConsoleUI.print_info("Generando gráfico...")
            self.graphics_service.plot_status_trend_over_time(self.current_simulated_file)
        except Exception as e:
            ConsoleUI.print_error(f"Error al generar gráfico: {str(e)}")
            input("\nPresione Enter para continuar...")
    
    def plot_multiple(self) -> None:
        """Muestra 4 gráficos juntos."""
        if not self._check_simulated_file():
            return
        
        ConsoleUI.clear_screen()
        ConsoleUI.print_header("🎯 MOSTRAR 4 GRÁFICOS JUNTOS")
        
        # Mostrar opciones de gráficos disponibles
        chart_options = {
            1: "Tareas por Prioridad",
            2: "Tareas por Estado",
            3: "Distribución Temporal",
            4: "Prioridad vs Estado (heatmap)",
            5: "Proporción por Prioridad (pie)",
            6: "Proporción por Estado (pie)",
            7: "Tendencia de Estados (stackplot)"
        }
        
        ConsoleUI.print_highlight("\nGráficos disponibles:")
        for idx, name in chart_options.items():
            print(f"{idx}. {name}")
        
        # Solicitar selección de 4 gráficos
        selected_charts = []
        for i in range(4):
            while True:
                choice = input(f"\nSeleccione el gráfico #{i+1} (1-7): ").strip()
                
                try:
                    chart_idx = int(choice)
                    if 1 <= chart_idx <= 7:
                        selected_charts.append(chart_idx)
                        ConsoleUI.print_success(f"✓ Gráfico seleccionado: {chart_options[chart_idx]}")
                        break
                    else:
                        ConsoleUI.print_error("Ingrese un número entre 1 y 7.")
                except ValueError:
                    ConsoleUI.print_error("Ingrese un número válido.")
        
        # Generar gráficos
        try:
            ConsoleUI.print_info("\nGenerando dashboard con 4 gráficos...")
            self.graphics_service.plot_multiple_charts(self.current_simulated_file, selected_charts)
        except Exception as e:
            ConsoleUI.print_error(f"Error al generar gráficos: {str(e)}")
            input("\nPresione Enter para continuar...")
    
    def exit_simulator(self) -> None:
        """Sale del simulador."""
        self.running = False
