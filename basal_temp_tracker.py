d
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
