import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, datetime, timedelta

class BasalTempTracker:
    def __init__(self):
        self.temps = {}
        self.day_counter = 1
        self.temp_list = []
        self.db_config = {
            'host': '192.168.64.3',  # IP específica del contenedor Docker
            'user': 'jul',  # Usuario correcto
            'password': 'J1GtOVw7og3RtgzJSroLiYXFLmeScjGOcMt',  # Contraseña correcta
            'database': 'apache_db',  # Nombre correcto de la base de datos
            'port': 3306
        }
        self.settings = {
            'fertile_temp': 98.0,
            'cycle_length': 28,
            'temperature_unit': 'F'
        }
        self.load_data()

    def get_db_connection(self):
        """Establece conexión con la base de datos"""
        try:
            print(f"Intentando conectar a MySQL: host={self.db_config['host']}, puerto={self.db_config.get('port', 3306)}")
            conn = mysql.connector.connect(**self.db_config)
            if conn.is_connected():
                print("Conexión exitosa a MySQL")
            return conn
        except mysql.connector.Error as e:
            print(f"Error de conexión a MySQL: {e}")
            if hasattr(e, 'errno'):
                if e.errno == 1045:  # Error de acceso denegado
                    print("Error de usuario o contraseña")
                elif e.errno == 1049:  # Base de datos desconocida
                    print("La base de datos no existe")
                elif e.errno == 2003:  # No se puede conectar
                    print("No se puede conectar al servidor MySQL. Verifique la dirección y puerto.")
            return None
        except Exception as e:
            print(f"Error inesperado de conexión a la base de datos: {e}")
            return None

    def init_db(self):
        """Inicializa la estructura de la base de datos si no existe"""
        conn = self.get_db_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            
            # Crear tabla de temperaturas si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS temperatures (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE UNIQUE,
                    temperature DECIMAL(4,2),
                    is_period BOOLEAN DEFAULT FALSE,
                    cycle_day INT,
                    mucus_type VARCHAR(50),
                    mood VARCHAR(50),
                    comment TEXT
                )
            """)
            
            # Crear tabla para el contador de ciclo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cycle_counter (
                    id INT PRIMARY KEY DEFAULT 1,
                    day_counter INT DEFAULT 1
                )
            """)
            
            # Insertar contador inicial si no existe
            cursor.execute("SELECT COUNT(*) FROM cycle_counter")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO cycle_counter VALUES (1, 1)")
            
            # Crear tabla para registros de ciclos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cycle_records (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    start_date DATE,
                    end_date DATE,
                    duration INT
                )
            """)
            
            # Crear tabla para configuraciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INT PRIMARY KEY DEFAULT 1,
                    cycle_length INT DEFAULT 28,
                    temperature_unit VARCHAR(1) DEFAULT 'F',
                    fertile_temp DECIMAL(4,2) DEFAULT 98.0,
                    shortest_cycle INT DEFAULT 25,
                    longest_cycle INT DEFAULT 35
                )
            """)
            
            # Insertar configuración inicial si no existe
            cursor.execute("SELECT COUNT(*) FROM settings")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                    INSERT INTO settings 
                    (cycle_length, temperature_unit, fertile_temp, shortest_cycle, longest_cycle) 
                    VALUES (28, 'F', 98.0, 25, 35)
                """)
            
            conn.commit()
            return True
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def load_settings(self):
        """Carga configuraciones desde la base de datos"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM settings LIMIT 1")
            settings = cursor.fetchone()
            
            if settings:
                self.settings = settings
                return True
            return False
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def load_data(self):
        """Carga datos desde la base de datos"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Cargar contador de días del ciclo
            cursor.execute("SELECT day_counter FROM cycle_counter LIMIT 1")
            counter_data = cursor.fetchone()
            if counter_data:
                self.day_counter = counter_data['day_counter']
            
            # Cargar temperaturas
            cursor.execute("SELECT date, temperature, cycle_day FROM temperatures ORDER BY date")
            temp_data = cursor.fetchall()
            
            self.temps = {}
            self.temp_list = []
            
            for record in temp_data:
                if record['cycle_day']:
                    self.temps[record['cycle_day']] = float(record['temperature'])
                self.temp_list.append(float(record['temperature']))
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def add_temp(self, temp, record_date=None, is_period=False, mucus_type=None, mood=None, comment=None):
        """Agrega una temperatura al registro"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Usar la fecha actual si no se proporciona
            if not record_date:
                record_date = date.today()
            elif isinstance(record_date, str):
                record_date = datetime.datetime.strptime(record_date, '%Y-%m-%d').date()
            
            # Si es un día de período, el día del ciclo es 1
            if is_period:
                cycle_day = 1
            else:
                # Buscar la fecha de período más reciente anterior a esta fecha
                cursor.execute("""
                    SELECT date
                    FROM temperatures
                    WHERE is_period = 1 AND date <= %s
                    ORDER BY date DESC
                    LIMIT 1
                """, (record_date,))
                
                last_period = cursor.fetchone()
                
                if last_period:
                    # Calcular días desde el último período
                    cycle_day = (record_date - last_period['date']).days + 1
                else:
                    # Si no hay período anterior, usar el contador actual
                    cycle_day = self.day_counter
                    
                print(f"Día del ciclo calculado: {cycle_day} para la fecha {record_date}")
            
            # Convertir temperatura a float
            temp_value = float(temp)
            
            # Verificar si ya existe un registro para esta fecha
            cursor.execute("SELECT id FROM temperatures WHERE date = %s", (record_date,))
            existing_record = cursor.fetchone()
            
            if existing_record:
                # Actualizar registro existente
                cursor.execute("""
                    UPDATE temperatures 
                    SET temperature = %s, is_period = %s, cycle_day = %s, mucus_type = %s, mood = %s, comment = %s
                    WHERE date = %s
                """, (temp_value, is_period, cycle_day, mucus_type, mood, comment, record_date))
            else:
                # Insertar nuevo registro
                cursor.execute("""
                    INSERT INTO temperatures 
                    (date, temperature, is_period, cycle_day, mucus_type, mood, comment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (record_date, temp_value, is_period, cycle_day, mucus_type, mood, comment))
            
            # Si es un día de período, actualizar el contador solo si es la fecha de hoy
            if is_period and record_date == date.today():
                cursor.execute("UPDATE cycle_counter SET day_counter = 1")
                self.day_counter = 1
            else:
                # Actualizar el contador solo si el registro es para hoy y no es período
                if record_date == date.today() and not is_period:
                    # Actualizar el contador de días basado en el día del ciclo calculado
                    cursor.execute("UPDATE cycle_counter SET day_counter = %s", (cycle_day,))
                    self.day_counter = cycle_day
            
            conn.commit()
            
            # Actualizar datos locales
            self.temps[cycle_day] = temp_value
            self.temp_list.append(temp_value)
            
            return True
            
        except Exception as e:
            print(f"Error adding temperature: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def reset_day_counter(self):
        """Reinicia el contador de días del ciclo"""
        conn = self.get_db_connection()
        if not conn:
            return False
            
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE cycle_counter SET day_counter = 1")
            conn.commit()
            
            self.day_counter = 1
            return True
            
        except Exception as e:
            print(f"Error resetting counter: {e}")
            return False
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_average(self, temp_list):
        """Calcula el promedio de temperaturas"""
        if not temp_list:
            return 0.0
        return sum(temp_list) / len(temp_list)

    def analyze(self):
        """Analiza los datos del ciclo actual"""
        conn = self.get_db_connection()
        if not conn:
            return {}
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Obtener últimos 30 días de datos
            cursor.execute("""
                SELECT date, temperature, is_period, cycle_day
                FROM temperatures
                ORDER BY date DESC
                LIMIT 30
            """)
            
            records = cursor.fetchall()
            
            if not records:
                return {
                    'average_temp': 0,
                    'fertile_days': [],
                    'infertile_days': [],
                    'day_count': 0
                }
            
            # Convertir temperaturas a float
            temps = [float(r['temperature']) for r in records]
            
            # Calcular promedio
            avg_temp = self.get_average(temps)
            
            # Determinar días fértiles (temperatura >= umbral fértil)
            fertile_temp = float(self.settings.get('fertile_temp', 98.0))
            
            fertile_days = []
            infertile_days = []
            
            for record in records:
                if float(record['temperature']) >= fertile_temp:
                    fertile_days.append(record['cycle_day'])
                else:
                    infertile_days.append(record['cycle_day'])
            
            return {
                'average_temp': round(avg_temp, 2),
                'fertile_days': fertile_days,
                'infertile_days': infertile_days,
                'day_count': len(records)
            }
            
        except Exception as e:
            print(f"Error analyzing data: {e}")
            return {}
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_temp_history(self):
        """Obtiene historial de temperaturas"""
        conn = self.get_db_connection()
        if not conn:
            print("Error: No se pudo establecer conexión a la base de datos en get_temp_history")
            return []
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Imprimir tablas disponibles para debug
            try:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                print("Tablas disponibles en la base de datos:", tables)
            except Exception as table_error:
                print(f"Error al listar tablas: {table_error}")
            
            query = """
                SELECT date, temperature, is_period, cycle_day, mucus_type, mood, comment
                FROM temperatures
                ORDER BY date DESC
                LIMIT 90
            """
            print("Ejecutando consulta:", query)
            
            cursor.execute(query)
            
            records = cursor.fetchall()
            print(f"Registros encontrados: {len(records)}")
            
            # Formatear registros para devolverlos
            history = []
            for record in records:
                history.append({
                    'date': record['date'].strftime('%Y-%m-%d'),
                    'temperature': float(record['temperature']),
                    'is_period': bool(record['is_period']),
                    'cycle_day': record['cycle_day'],  # Mantener cycle_day para consistencia interna
                    'day': record['cycle_day'],  # Agregar day para compatibilidad con la plantilla
                    'mucus_type': record['mucus_type'],
                    'mood': record['mood'],
                    'comment': record['comment']
                })
            
            print(f"Historial formateado con {len(history)} registros")
            return history
            
        except Exception as e:
            print(f"Error en get_temp_history: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
                print("Conexión cerrada en get_temp_history")

    def get_chart_data(self, cycle_id=None):
        """Obtiene datos para gráficos"""
        conn = self.get_db_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            if cycle_id and cycle_id != 'all':
                # Obtener datos para un ciclo específico
                cursor.execute("""
                    SELECT cr.start_date, cr.end_date
                    FROM cycle_records cr
                    WHERE cr.id = %s
                """, (cycle_id,))
                
                cycle = cursor.fetchone()
                if not cycle:
                    return None
                
                cursor.execute("""
                    SELECT date, temperature, is_period, cycle_day
                    FROM temperatures
                    WHERE date BETWEEN %s AND %s
                    ORDER BY date
                """, (cycle['start_date'], cycle['end_date']))
                
            elif cycle_id == 'all':
                # Obtener todos los datos
                cursor.execute("""
                    SELECT date, temperature, is_period, cycle_day
                    FROM temperatures
                    ORDER BY date
                """)
                
            else:
                # Obtener datos del ciclo actual
                # Primero encontrar el inicio del ciclo actual
                cursor.execute("""
                    SELECT date
                    FROM temperatures
                    WHERE is_period = 1
                    ORDER BY date DESC
                    LIMIT 1
                """)
                
                latest_period = cursor.fetchone()
                if not latest_period:
                    return None
                
                cursor.execute("""
                    SELECT date, temperature, is_period, cycle_day
                    FROM temperatures
                    WHERE date >= %s
                    ORDER BY date
                """, (latest_period['date'],))
            
            temp_records = cursor.fetchall()
            
            if not temp_records:
                return None
            
            # Formatear datos para el gráfico en el formato esperado por cycle-chart.js
            xAxis = []  # Días del ciclo (cycle_day)
            tempData = []  # Temperaturas
            isPeriod = []  # Si es día de período
            dates = []  # Fechas en formato string
            
            for record in temp_records:
                xAxis.append(record['cycle_day'])
                tempData.append(float(record['temperature']))
                dates.append(record['date'].strftime('%Y-%m-%d'))
                isPeriod.append(bool(record['is_period']))
            
            # Calcular estadísticas
            fertile_temp = float(self.settings.get('fertile_temp', 98.0))
            
            # Calcular la ventana fértil usando mejores criterios:
            # 1. Basada en el día del ciclo (días 10-17)
            # 2. Considerando el cambio de temperatura (día de ovulación)
            
            # Detectar cambio de temperatura significativo (posible día de ovulación)
            ovulation_day = None
            fertile_window_start = None
            fertile_window_end = None
            
            # Método 1: Detección del día de ovulación basada en el cambio de temperatura
            if len(tempData) >= 6:  # Necesitamos suficientes datos para detectar un patrón
                for i in range(2, len(tempData) - 2):  # Ignorar los primeros y últimos días
                    # Calcular promedio de 3 días antes y después
                    before_avg = sum(tempData[max(0, i-3):i]) / min(3, i)
                    after_avg = sum(tempData[i:min(len(tempData), i+3)]) / min(3, len(tempData) - i)
                    
                    # Si hay un aumento significativo (>0.2°F) y estamos en días 8-20
                    if (after_avg - before_avg) > 0.2 and 8 <= xAxis[i] <= 20:
                        ovulation_day = xAxis[i]
                        # La ventana fértil es normalmente 5 días antes y 1 día después de la ovulación
                        fertile_window_start = max(1, ovulation_day - 5)
                        fertile_window_end = min(ovulation_day + 1, max(xAxis))
                        break
            
            # Método 2: Si no se detectó ovulación, usar el método tradicional basado en el día del ciclo
            if not ovulation_day:
                if max(xAxis) >= 10:  # Si el ciclo tiene al menos 10 días
                    cycle_length = max(xAxis)
                    # Para ciclos cortos (menos de 28 días), ajustar la ventana
                    if cycle_length < 28:
                        adjustment = (28 - cycle_length) // 2
                        fertile_window_start = max(1, 10 - adjustment)
                        fertile_window_end = min(cycle_length, 17 - adjustment)
                    else:
                        fertile_window_start = 10
                        fertile_window_end = min(cycle_length, 17)
            
            # Generar lista de días fértiles para la visualización
            fertileDays = []
            
            if fertile_window_start and fertile_window_end:
                for day in xAxis:
                    if fertile_window_start <= day <= fertile_window_end:
                        fertileDays.append(day)
            
            # Como respaldo, incluir también días con temperatura alta
            temp_based_fertile_days = []
            for i, temp in enumerate(tempData):
                if temp >= fertile_temp:
                    temp_based_fertile_days.append(xAxis[i])
            
            # Si no detectamos ventana fértil por ningún método, usar los basados en temperatura
            if not fertileDays:
                fertileDays = temp_based_fertile_days
            
            # Incluir tanto formato antiguo como nuevo para compatibilidad
            return {
                # Formato antiguo
                'days': xAxis,
                'temperatures': tempData,
                'dates': dates,
                'periodDays': [day for i, day in enumerate(xAxis) if isPeriod[i]],
                'fertileThreshold': fertile_temp,
                
                # Formato nuevo esperado por cycle-chart.js
                'xAxis': xAxis,
                'tempData': tempData,
                'isPeriod': isPeriod,
                'fertileDays': fertileDays,
                'ovulationDay': ovulation_day
            }
            
        except Exception as e:
            print(f"Error getting chart data: {e}")
            return None
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_current_cycle_data(self):
        """Obtiene datos del ciclo actual"""
        conn = self.get_db_connection()
        if not conn:
            return None
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Encontrar el inicio del ciclo actual
            cursor.execute("""
                SELECT date
                FROM temperatures
                WHERE is_period = 1
                ORDER BY date DESC
                LIMIT 1
            """)
            
            latest_period = cursor.fetchone()
            if not latest_period:
                return None
            
            cursor.execute("""
                SELECT date, temperature, is_period, cycle_day, mucus_type, mood, comment
                FROM temperatures
                WHERE date >= %s
                ORDER BY date
            """, (latest_period['date'],))
            
            records = cursor.fetchall()
            
            if not records:
                return None
            
            # Formatear datos para el ciclo actual
            days = []
            temps = []
            dates = []
            is_period = []
            mucus_types = []
            moods = []
            comments = []
            
            for record in records:
                days.append(record['cycle_day'])
                temps.append(float(record['temperature']))
                dates.append(record['date'].strftime('%Y-%m-%d'))
                is_period.append(bool(record['is_period']))
                mucus_types.append(record['mucus_type'])
                moods.append(record['mood'])
                comments.append(record['comment'])
            
            # Calcular estadísticas
            fertile_temp = float(self.settings.get('fertile_temp', 98.0))
            
            # Calcular la ventana fértil usando mejores criterios
            # 1. Basada en el día del ciclo (días 10-17)
            # 2. Considerando el cambio de temperatura (día de ovulación)
            
            # Detectar cambio de temperatura significativo (posible día de ovulación)
            ovulation_day = None
            fertile_window_start = None
            fertile_window_end = None
            
            # Método 1: Detección del día de ovulación basada en el cambio de temperatura
            if len(temps) >= 6:  # Necesitamos suficientes datos para detectar un patrón
                for i in range(2, len(temps) - 2):  # Ignorar los primeros y últimos días
                    # Calcular promedio de 3 días antes y después
                    before_avg = sum(temps[max(0, i-3):i]) / min(3, i)
                    after_avg = sum(temps[i:min(len(temps), i+3)]) / min(3, len(temps) - i)
                    
                    # Si hay un aumento significativo (>0.2°F) y estamos en días 8-20
                    if (after_avg - before_avg) > 0.2 and 8 <= days[i] <= 20:
                        ovulation_day = days[i]
                        # La ventana fértil es normalmente 5 días antes y 1 día después de la ovulación
                        fertile_window_start = max(1, ovulation_day - 5)
                        fertile_window_end = min(ovulation_day + 1, max(days))
                        break
            
            # Método 2: Si no se detectó ovulación, usar el método tradicional basado en el día del ciclo
            if not ovulation_day:
                if max(days) >= 10:  # Si el ciclo tiene al menos 10 días
                    cycle_length = max(days)
                    # Para ciclos cortos (menos de 28 días), ajustar la ventana
                    if cycle_length < 28:
                        adjustment = (28 - cycle_length) // 2
                        fertile_window_start = max(1, 10 - adjustment)
                        fertile_window_end = min(cycle_length, 17 - adjustment)
                    else:
                        fertile_window_start = 10
                        fertile_window_end = min(cycle_length, 17)
            
            # Generar lista de días fértiles para la visualización
            fertile_days = []
            
            if fertile_window_start and fertile_window_end:
                for day in days:
                    if fertile_window_start <= day <= fertile_window_end:
                        fertile_days.append(day)
            
            # Como respaldo, incluir también días con temperatura alta
            if not fertile_days:
                for i, temp in enumerate(temps):
                    if temp >= fertile_temp:
                        fertile_days.append(days[i])
            
            return {
                'days': days,
                'temperatures': temps,
                'dates': dates,
                'isPeriod': is_period,
                'mucusTypes': mucus_types,
                'moods': moods,
                'comments': comments,
                'currentDay': self.day_counter,
                'fertileDays': fertile_days,
                'fertileThreshold': fertile_temp,
                'ovulationDay': ovulation_day
            }
            
        except Exception as e:
            print(f"Error getting current cycle data: {e}")
            return None
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_cycle_records(self):
        """Obtiene registros de ciclos"""
        conn = self.get_db_connection()
        if not conn:
            return []
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT id, start_date, end_date, duration
                FROM cycle_records
                ORDER BY start_date DESC
                LIMIT 12
            """)
            
            records = cursor.fetchall()
            
            # Formatear registros para devolverlos
            formatted_records = []
            for record in records:
                formatted_records.append({
                    'id': record['id'],
                    'start_date': record['start_date'].strftime('%Y-%m-%d'),
                    'end_date': record['end_date'].strftime('%Y-%m-%d'),
                    'duration': record['duration']
                })
            
            return formatted_records
            
        except Exception as e:
            print(f"Error getting cycle records: {e}")
            return []
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def mark_period(self, day, is_period):
        """Marca un día como período o no"""
        conn = self.get_db_connection()
        if not conn:
            return (False, "Error de conexión a la base de datos")
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Obtener la fecha correspondiente al día del ciclo
            cursor.execute("""
                SELECT date
                FROM temperatures
                WHERE cycle_day = %s
                ORDER BY date DESC
                LIMIT 1
            """, (day,))
            
            day_record = cursor.fetchone()
            
            if not day_record:
                return (False, f"No se encontró ningún registro para el día {day} del ciclo")
            
            # Actualizar el registro
            cursor.execute("""
                UPDATE temperatures
                SET is_period = %s
                WHERE date = %s
            """, (is_period, day_record['date']))
            
            conn.commit()
            
            status = "marcado como" if is_period else "desmarcado como"
            return (True, f"Día {day} {status} día de período")
            
        except Exception as e:
            print(f"Error marking period day: {e}")
            return (False, f"Error al marcar el día: {str(e)}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def get_average_cycle_length(self):
        """Calcula la duración promedio del ciclo"""
        conn = self.get_db_connection()
        if not conn:
            return 28
            
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT AVG(duration) as avg_duration
                FROM cycle_records
            """)
            
            result = cursor.fetchone()
            
            if result and result[0]:
                return round(result[0])
            return 28
            
        except Exception as e:
            print(f"Error calculating average cycle length: {e}")
            return 28
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def synchronize_cycle(self):
        """Sincroniza los días del ciclo con las fechas reales"""
        conn = self.get_db_connection()
        if not conn:
            return (False, "Error de conexión a la base de datos")
            
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Obtener todos los períodos ordenados por fecha
            cursor.execute("""
                SELECT date
                FROM temperatures
                WHERE is_period = 1
                ORDER BY date
            """)
            
            periods = cursor.fetchall()
            
            if not periods:
                return (False, "No hay días de período para sincronizar")
            
            # Actualizar los días del ciclo para cada período
            for i in range(len(periods)):
                period_date = periods[i]['date']
                
                # Si hay un siguiente período, usar esa fecha como límite
                if i < len(periods) - 1:
                    next_period = periods[i+1]['date']
                    
                    # Actualizar los días del ciclo para este rango
                    cursor.execute("""
                        UPDATE temperatures
                        SET cycle_day = DATEDIFF(date, %s) + 1
                        WHERE date >= %s AND date < %s
                    """, (period_date, period_date, next_period))
                else:
                    # Para el último período hasta hoy
                    cursor.execute("""
                        UPDATE temperatures
                        SET cycle_day = DATEDIFF(date, %s) + 1
                        WHERE date >= %s
                    """, (period_date, period_date))
            
            # Actualizar el contador actual basado en el último período
            today = date.today()
            last_period = periods[-1]['date']
            day_counter = (today - last_period).days + 1
            
            cursor.execute("UPDATE cycle_counter SET day_counter = %s", (day_counter,))
            self.day_counter = day_counter
            
            conn.commit()
            
            return (True, f"Ciclo sincronizado. Día actual: {day_counter}")
            
        except Exception as e:
            print(f"Error synchronizing cycle: {e}")
            return (False, f"Error al sincronizar el ciclo: {str(e)}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def fix_historical_data(self):
        """Corrige datos históricos del ciclo"""
        # Método para corregir datos inconsistentes
        # Esta es una implementación básica
        return self.synchronize_cycle()

    def plot_data(self):
        """Visualiza los datos de temperatura (para consola)"""
        # Método para visualización en línea de comandos
        # No se usa en la aplicación web
        pass 