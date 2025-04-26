from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import datetime
from datetime import timedelta, date
import json
import mysql.connector

from basal_temp_tracker import BasalTempTracker

# Initialize Flask app
app = Flask(__name__)
app.secret_key = '12345678901234567890'

# Ensure static directory exists
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), exist_ok=True)

# Initialize tracker
tracker = BasalTempTracker()

# Call init_db to ensure database structure is correct

# Load settings

@app.route('/')
def index():
    try:
        analysis = tracker.analyze()
        
        # Asegurarnos de que analysis siempre tenga average_temp
        if not analysis:
            analysis = {"average_temp": 0, "fertile_days": [], "infertile_days": [], "day_count": 0}
        elif 'average_temp' not in analysis:
            analysis['average_temp'] = 0
            
        chart_data = tracker.get_chart_data()
        current_cycle_data = tracker.get_current_cycle_data()
        cycle_records = tracker.get_cycle_records()
        
        # Garantizar valores predeterminados si no hay datos
        if chart_data is None:
            chart_data = {"days": [], "temperatures": [], "dates": [], "periodDays": []}
            
        if current_cycle_data is None:
            current_cycle_data = {}
            
        if cycle_records is None:
            cycle_records = []
            
        # Debug para entender la estructura
        if current_cycle_data:
            print("Current Cycle Data:", current_cycle_data)
        
        return render_template('index.html', 
                            day_counter=tracker.day_counter,
                            analysis=analysis,
                            chart_data=json.dumps(chart_data) if chart_data else "{}",
                            current_cycle_data=json.dumps(current_cycle_data) if current_cycle_data else "{}",
                            cycle_records=cycle_records)
    except Exception as e:
        # Registrar el error y mostrar una página con mensaje amigable
        print(f"Error en la página principal: {e}")
        empty_analysis = {"average_temp": 0, "fertile_days": [], "infertile_days": [], "day_count": 0}
        return render_template('index.html', 
                            day_counter=1,
                            analysis=empty_analysis,
                            chart_data="{}",
                            current_cycle_data="{}",
                            cycle_records=[],
                            error_message="Hubo un problema al cargar los datos. Por favor intente de nuevo.")

@app.route('/history')
def history():
    try:
        print("Iniciando carga de historial de temperaturas...")
        temp_history = tracker.get_temp_history()
        cycle_records = tracker.get_cycle_records()
        
        # Garantizar que tenemos datos válidos
        if temp_history is None:
            temp_history = []
            print("No se obtuvieron datos de historial (None)")
        elif len(temp_history) == 0:
            print("No hay datos en el historial (lista vacía)")
        else:
            print(f"Se obtuvieron {len(temp_history)} registros de historial")
        
        if cycle_records is None:
            cycle_records = []
            
        # Intentar conectar directamente a la base de datos para diagnóstico
        try:
            db_config = {
                'host': '192.168.64.3',
                'user': 'jul',
                'password': 'J1GtOVw7og3RtgzJSroLiYXFLmeScjGOcMt',
                'database': 'apache_db',
                'port': 3306
            }
            print(f"Intentando conexión directa a MySQL: {db_config['host']}, db: {db_config['database']}")
            conn = mysql.connector.connect(**db_config)
            
            if conn.is_connected():
                print("Conexión directa a MySQL exitosa")
                cursor = conn.cursor(dictionary=True)
                
                # Verificar si existe la tabla temperatures
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                
                print(f"Tablas encontradas: {tables}")
                
                table_exists = False
                for table in tables:
                    table_name = list(table.values())[0]
                    if table_name == 'temperatures':
                        table_exists = True
                        break
                
                if table_exists:
                    cursor.execute("SELECT COUNT(*) as count FROM temperatures")
                    result = cursor.fetchone()
                    print(f"Cantidad de registros en temperatures: {result['count']}")
                else:
                    error_message = "La tabla 'temperatures' no existe en la base de datos."
                    print(error_message)
                    return render_template('history.html', 
                                        temp_history=[],
                                        cycle_records=[],
                                        error_message=error_message)
                
                cursor.close()
                conn.close()
            
        except Exception as db_error:
            error_message = f"Error al conectar directamente a la base de datos: {db_error}"
            print(error_message)
            import traceback
            traceback.print_exc()
            return render_template('history.html', 
                                temp_history=[],
                                cycle_records=[],
                                error_message=error_message)
            
        return render_template('history.html', 
                            temp_history=temp_history,
                            cycle_records=cycle_records)
    except Exception as e:
        # Registrar el error y mostrar una página con mensaje amigable
        error_message = f"Error al cargar historial: {e}"
        print(error_message)
        import traceback
        traceback.print_exc()
        return render_template('history.html', 
                            temp_history=[],
                            cycle_records=[],
                            error_message=error_message)

@app.route('/add_temp', methods=['POST'])
def add_temp():
    try:
        temp = request.form.get('temperature')
        date_str = request.form.get('date')
        is_period = 'is_period' in request.form
        mucus_type = request.form.get('mucus_type')
        mood = request.form.get('mood')
        comment = request.form.get('comment')
        
        # Diagnóstico inicial
        print(f"Datos recibidos: temp={temp}, fecha={date_str}, periodo={is_period}, mucus={mucus_type}")
        
        if not temp:
            flash("Temperature is required", "danger")
            return redirect(url_for('index'))
        
        # Parse the date if provided, otherwise use today's date
        record_date = None
        if date_str:
            try:
                record_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                print(f"Fecha parseada: {record_date}")
            except ValueError as e:
                print(f"Error al parsear fecha: {e}")
                flash("Invalid date format", "danger")
                return redirect(url_for('index'))
        else:
            record_date = date.today()
            print(f"Usando fecha actual: {record_date}")
        
        # Special handling for period days - if marking a past date as period
        # we need to ensure cycle days are updated correctly
        if is_period:
            print("Procesando día marcado como período")
            # Check if this is a new period start date
            conn = tracker.get_db_connection()
            if not conn:
                print("Error: No se pudo conectar a la base de datos para procesar período")
                flash("Database connection error", "danger")
                return redirect(url_for('index'))
                
            try:
                cursor = conn.cursor(dictionary=True)
                # Find the most recent period date before this one
                cursor.execute("""
                    SELECT date
                    FROM temperatures
                    WHERE is_period = 1 AND date < %s
                    ORDER BY date DESC
                    LIMIT 1
                """, (record_date,))
                
                prev_period = cursor.fetchone()
                print(f"Período anterior: {prev_period}")
                
                # Find the next period date after this one
                cursor.execute("""
                    SELECT date
                    FROM temperatures
                    WHERE is_period = 1 AND date > %s
                    ORDER BY date ASC
                    LIMIT 1
                """, (record_date,))
                
                next_period = cursor.fetchone()
                print(f"Período siguiente: {next_period}")
                
                # If this creates a new period between existing periods,
                # we need to update cycle days for all affected records
                if prev_period:
                    # Records that need updates are those between prev_period and record_date
                    end_date = next_period['date'] if next_period else date.today()
                    print(f"Actualizando registros entre {record_date} y {end_date}")
                    
                    cursor.execute("""
                        SELECT id, date
                        FROM temperatures
                        WHERE date >= %s AND date <= %s
                        ORDER BY date ASC
                    """, (record_date, end_date))
                    
                    records_to_update = cursor.fetchall()
                    print(f"Registros a actualizar: {len(records_to_update)}")
                    
                    # Update cycle days for these records
                    for update_record in records_to_update:
                        update_date = update_record['date']
                        days_since_period = (update_date - record_date).days + 1
                        
                        cursor.execute("""
                            UPDATE temperatures
                            SET cycle_day = %s
                            WHERE id = %s
                        """, (days_since_period, update_record['id']))
                    
                    conn.commit()
            except Exception as e:
                print(f"Error al actualizar días del ciclo: {e}")
                import traceback
                traceback.print_exc()
                flash(f"Error updating cycle days: {str(e)}", "danger")
                return redirect(url_for('index'))
            finally:
                cursor.close()
                conn.close()
        
        print(f"Llamando a tracker.add_temp con temperatura {temp} para la fecha {record_date}")
        # Add the temperature record
        result = tracker.add_temp(temp, record_date, is_period, mucus_type, mood, comment)
        
        if result:
            flash("Temperature recorded successfully!", "success")
        else:
            flash("Error recording temperature", "danger")
            return redirect(url_for('index'))
        
        # If we marked today as a period day, make sure we run the fix
        # cycle days function to update everything
        if is_period and record_date == date.today():
            print("Actualizando contador de ciclo para día de período")
            # Directly run the fix cycle days logic
            connection = tracker.get_db_connection()
            if not connection:
                print("Error: No se pudo conectar a la base de datos para actualizar contador de ciclo")
                flash("Database connection error when updating cycle counter", "danger")
                return redirect(url_for('index'))
                
            try:
                cursor = connection.cursor(dictionary=True)
                # Update cycle counter
                today = date.today()
                cursor.execute("UPDATE cycle_counter SET day_counter = 1")
                tracker.day_counter = 1
                
                # Also update any cycle records
                cursor.execute("""
                    SELECT id
                    FROM cycle_records
                    WHERE start_date = %s
                """, (today,))
                
                cycle_record = cursor.fetchone()
                if not cycle_record:
                    # Create a new cycle record starting today
                    cursor.execute("""
                        INSERT INTO cycle_records (start_date, end_date, duration)
                        VALUES (%s, %s, %s)
                    """, (today, today, 1))
                
                connection.commit()
            except Exception as e:
                print(f"Error al actualizar contador de ciclo: {e}")
                import traceback
                traceback.print_exc()
                flash(f"Error updating cycle counter: {str(e)}", "danger")
                return redirect(url_for('index'))
            finally:
                cursor.close()
                connection.close()
        
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error general en add_temp: {e}")
        import traceback
        traceback.print_exc()
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/reset_cycle', methods=['POST'])
def reset_cycle():
    if tracker.reset_day_counter():
        flash('Menstrual cycle counter has been reset.', 'success')
    else:
        flash('Error resetting cycle. Please check the database connection.', 'error')
    return redirect(url_for('index'))

@app.route('/mark_period/<int:day>', methods=['POST'])
def mark_period(day):
    is_period = request.form.get('is_period', 'true') == 'true'
    
    # Call the updated mark_period method which now returns success and message
    success, message = tracker.mark_period(day, is_period)
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    # Check if the request came from the history page
    referrer = request.referrer
    if referrer and 'history' in referrer:
        return redirect(url_for('history'))
    return redirect(url_for('index'))

@app.route('/api/analysis', methods=['GET'])
def api_analysis():
    return jsonify(tracker.analyze())

@app.route('/api/temperature_history', methods=['GET'])
def api_temp_history():
    return jsonify(tracker.get_temp_history())

@app.route('/api/chart_data', methods=['GET'])
def api_chart_data():
    return jsonify(tracker.get_chart_data())

@app.route('/api/chart_data/<cycle_id>', methods=['GET'])
def api_chart_data_by_cycle(cycle_id):
    # Check if we're asking for all cycles
    if cycle_id == 'all':
        data = tracker.get_chart_data('all')
    else:
        try:
            # Try to convert to integer if not 'all'
            cycle_id = int(cycle_id)
            data = tracker.get_chart_data(cycle_id)
        except ValueError:
            return jsonify({"error": "Invalid cycle ID. Must be 'all' or a number."}), 400
    
    if data:
        return jsonify(data)
    return jsonify({"error": "No data available for this cycle"}), 404

@app.route('/api/current_cycle_data', methods=['GET'])
def api_current_cycle_data():
    return jsonify(tracker.get_current_cycle_data())

@app.route('/settings', methods=['GET'])
def settings():
    return render_template('settings.html', settings=tracker.settings)

@app.route('/save_settings', methods=['POST'])
def save_settings():
    try:
        # Obtain values from the form
        cycle_length = int(request.form.get('cycle_length', 28))
        temp_unit = request.form.get('temperature_unit', 'F')
        shortest_cycle = int(request.form.get('shortest_cycle', 28))
        longest_cycle = int(request.form.get('longest_cycle', 32))
        
        # Update settings in the database
        db = get_db()
        cursor = db.cursor()
        
        # Check if settings exist first
        cursor.execute("SELECT COUNT(*) FROM settings")
        has_settings = cursor.fetchone()[0] > 0
        
        if has_settings:
            cursor.execute(
                "UPDATE settings SET cycle_length = %s, temperature_unit = %s, shortest_cycle = %s, longest_cycle = %s",
                (cycle_length, temp_unit, shortest_cycle, longest_cycle)
            )
        else:
            cursor.execute(
                "INSERT INTO settings (cycle_length, temperature_unit, shortest_cycle, longest_cycle) VALUES (%s, %s, %s, %s)",
                (cycle_length, temp_unit, shortest_cycle, longest_cycle)
            )
        
        db.commit()
        flash('Settings saved successfully!', 'success')
    except Exception as e:
        flash(f'Error saving settings: {str(e)}', 'danger')
    
    return redirect(url_for('settings'))

@app.route('/cycles')
def cycles():
    cycle_records = tracker.get_cycle_records()
    avg_cycle_length = tracker.get_average_cycle_length()
    
    return render_template('cycles.html', 
                          cycle_records=cycle_records,
                          avg_cycle_length=avg_cycle_length,
                          day_counter=tracker.day_counter)

@app.route('/fix_data', methods=['POST'])
def fix_data():
    """Route to fix historical cycle data."""
    success, message = tracker.fix_historical_data()
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
        
    # Return to the history page
    return redirect(url_for('history'))

@app.route('/sync_cycle', methods=['POST'])
def sync_cycle():
    """Route to synchronize cycle data with actual dates."""
    success, message = tracker.synchronize_cycle()
    
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
        
    # Return to the page the request came from, or the index page
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for('index'))

@app.route('/api/cycle_analytics')
def cycle_analytics_api():
    """API endpoint for cycle analytics data."""
    try:
        connection = tracker.get_db_connection()
        if not connection:
            return jsonify({"error": "Database connection failed"}), 500
        
        cursor = connection.cursor(dictionary=True)
        
        # Get all cycle records
        cursor.execute("""
            SELECT * FROM cycle_records
            ORDER BY start_date ASC
        """)
        cycle_records = cursor.fetchall()
        
        if not cycle_records:
            return jsonify({
                "message": "No cycle data available",
                "cycles": [],
                "average_cycle_length": 28,
                "average_fertile_temp": float(tracker.settings.get('fertile_temp', 98.6)),
                "average_follicular_length": 14,
                "average_luteal_length": 14
            })
        
        # Prepare cycle data
        cycles_data = []
        
        # Calculate average cycle length
        total_length = sum(record['duration'] for record in cycle_records)
        avg_cycle_length = total_length / len(cycle_records)
        
        # Approximate follicular and luteal phase lengths (if we don't have ovulation data)
        avg_follicular_length = avg_cycle_length * 0.5
        avg_luteal_length = avg_cycle_length * 0.5
        
        # Get average fertile temperature
        fertile_temp = float(tracker.settings.get('fertile_temp', 98.6))
        
        # Get temperature data for each cycle
        for record in cycle_records:
            cursor.execute("""
                SELECT date, temperature, is_period, cycle_day
                FROM temperatures
                WHERE date BETWEEN %s AND %s
                ORDER BY date ASC
            """, (record['start_date'], record['end_date']))
            
            temp_data = cursor.fetchall()
            
            if temp_data:
                # Dates and temperatures arrays
                dates = [temp['date'].strftime('%Y-%m-%d') for temp in temp_data]
                temps = [float(temp['temperature']) for temp in temp_data]
                
                # Simple estimation of follicular phase (first half) and luteal phase (second half)
                follicular_length = len(temp_data) // 2
                
                # Find the temperature shift (if any)
                if len(temps) > 6:
                    first_half = temps[:follicular_length]
                    second_half = temps[follicular_length:]
                    
                    first_half_avg = sum(first_half) / len(first_half) if first_half else 0
                    second_half_avg = sum(second_half) / len(second_half) if second_half else 0
                    
                    temp_shift = second_half_avg - first_half_avg
                else:
                    temp_shift = 0
                
                cycles_data.append({
                    "id": record['id'],
                    "start_date": record['start_date'].strftime('%Y-%m-%d'),
                    "end_date": record['end_date'].strftime('%Y-%m-%d'),
                    "duration": record['duration'],
                    "follicular_phase_length": follicular_length,
                    "luteal_phase_length": len(temp_data) - follicular_length,
                    "temperature_shift": round(temp_shift, 2),
                    "dates": dates,
                    "temperatures": temps,
                    "average_temp": round(sum(temps) / len(temps), 2) if temps else 0
                })
        
        # Return the data
        return jsonify({
            "cycles": cycles_data,
            "average_cycle_length": round(avg_cycle_length, 1),
            "average_fertile_temp": fertile_temp,
            "average_follicular_length": round(avg_follicular_length, 1),
            "average_luteal_length": round(avg_luteal_length, 1)
        })
        
    except Error as e:
        print(f"Error in cycle analytics API: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/user_guide')
def user_guide():
    """Display the user guide for the mobile app."""
    return render_template('user_guide.html')

@app.route('/update_record', methods=['POST'])
def update_record():
    """Route to update a temperature record."""
    data = request.json
    
    if not data or 'date' not in data:
        return jsonify({"success": False, "message": "Missing date parameter"}), 400
    
    connection = tracker.get_db_connection()
    if not connection:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor()
        
        # Prepare update data
        update_fields = []
        update_values = []
        
        if 'temperature' in data and data['temperature']:
            try:
                temperature = float(data['temperature'])
                update_fields.append("temperature = %s")
                update_values.append(temperature)
            except ValueError:
                return jsonify({"success": False, "message": "Invalid temperature value"}), 400
        
        if 'comment' in data:
            update_fields.append("comment = %s")
            update_values.append(data['comment'])
            
        if 'mucus_type' in data:
            update_fields.append("mucus_type = %s")
            update_values.append(data['mucus_type'])
            
        if 'mood' in data:
            update_fields.append("mood = %s")
            update_values.append(data['mood'])
        
        if 'cycle_day' in data and data['cycle_day']:
            try:
                cycle_day = int(data['cycle_day'])
                if cycle_day < 1:
                    return jsonify({"success": False, "message": "Cycle day must be a positive number"}), 400
                update_fields.append("cycle_day = %s")
                update_values.append(cycle_day)
            except ValueError:
                return jsonify({"success": False, "message": "Invalid cycle day value"}), 400
        
        if not update_fields:
            return jsonify({"success": False, "message": "No fields to update"}), 400
        
        # Build and execute the update query
        query = f"UPDATE temperatures SET {', '.join(update_fields)} WHERE date = %s"
        update_values.append(data['date'])
        
        cursor.execute(query, update_values)
        connection.commit()
        
        # Limpiar caché para asegurar datos actualizados
        tracker.temps = {}
        
        return jsonify({"success": True, "message": "Record updated successfully"})
        
    except Error as e:
        print(f"Error updating record: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/delete_record', methods=['POST'])
def delete_record():
    """Route to delete a temperature record."""
    data = request.json
    
    if not data or 'date' not in data:
        return jsonify({"success": False, "message": "Missing date parameter"}), 400
    
    connection = tracker.get_db_connection()
    if not connection:
        return jsonify({"success": False, "message": "Database connection failed"}), 500
    
    try:
        cursor = connection.cursor()
        
        # Delete the record
        query = "DELETE FROM temperatures WHERE date = %s"
        cursor.execute(query, (data['date'],))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "Record not found"}), 404
        
        # Refresh cached data
        tracker.temps = {}
        
        # Check if we need to fix cycle days
        success, message = tracker.synchronize_cycle()
        
        return jsonify({"success": True, "message": "Record deleted successfully"})
        
    except Error as e:
        print(f"Error deleting record: {e}")
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

@app.route('/calculate_fertile_threshold', methods=['POST'])
def calculate_fertile_threshold():
    # Esta función ha sido deshabilitada ya que el cálculo del umbral fértil
    # se implementará de otra forma más analítica
    flash("Esta función ha sido deshabilitada. Se implementará un nuevo método para determinar días fértiles.", "info")
    return redirect(url_for('settings'))

@app.route('/fix_cycle_days', methods=['POST'])
def fix_cycle_days():
    """Recalcula y corrige los días del ciclo para todos los registros de temperatura."""
    connection = tracker.get_db_connection()
    if not connection:
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for('index'))
        
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Paso 1: Asegurarse de que todas las fechas tienen cycle_day y son únicas
        cursor.execute("""
            SELECT date, COUNT(*) as count
            FROM temperatures
            GROUP BY date
            HAVING COUNT(*) > 1
        """)
        
        duplicates = cursor.fetchall()
        if duplicates:
            # Eliminar registros duplicados, conservando solo uno para cada fecha
            for dup in duplicates:
                cursor.execute("""
                    SELECT id FROM temperatures
                    WHERE date = %s
                    ORDER BY id
                """, (dup['date'],))
                
                records = cursor.fetchall()
                # Conservar solo el primer registro (el más antiguo)
                for i in range(1, len(records)):
                    cursor.execute("DELETE FROM temperatures WHERE id = %s", (records[i]['id'],))
            
            flash(f"Se eliminaron {sum(d['count']-1 for d in duplicates)} registros duplicados.", "warning")
        
        # Paso 2: Obtener todos los períodos ordenados por fecha
        cursor.execute("""
            SELECT id, date
            FROM temperatures
            WHERE is_period = 1
            ORDER BY date ASC
        """)
        
        period_records = cursor.fetchall()
        
        if not period_records:
            flash("No se encontraron días de período para corregir los días del ciclo.", "warning")
            return redirect(url_for('index'))
        
        # Paso 3: Procesar cada período y actualizar los ciclos
        cycles_processed = 0
        records_updated = 0
        
        for i in range(len(period_records)):
            start_date = period_records[i]['date']
            
            # Si hay un siguiente período, usarlo como fin del ciclo actual
            if i < len(period_records) - 1:
                end_date = period_records[i+1]['date'] - timedelta(days=1)
            else:
                # Si es el último período, usar la fecha actual como fin
                end_date = date.today()
            
            # Obtener todos los registros en este ciclo
            cursor.execute("""
                SELECT id, date
                FROM temperatures
                WHERE date >= %s AND date <= %s
                ORDER BY date ASC
            """, (start_date, end_date))
            
            cycle_records = cursor.fetchall()
            
            # Actualizar cada registro con el día de ciclo correcto
            day_counter = 1
            for record in cycle_records:
                record_date = record['date']
                cycle_day = (record_date - start_date).days + 1
                
                cursor.execute("""
                    UPDATE temperatures
                    SET cycle_day = %s
                    WHERE id = %s
                """, (cycle_day, record['id']))
                
                records_updated += 1
            
            # Crear o actualizar el registro de ciclo
            cursor.execute("""
                SELECT id
                FROM cycle_records
                WHERE start_date = %s
            """, (start_date,))
            
            cycle_record = cursor.fetchone()
            
            # Calcular la duración del ciclo
            duration = (end_date - start_date).days + 1
            
            if cycle_record:
                # Actualizar el registro existente
                cursor.execute("""
                    UPDATE cycle_records
                    SET end_date = %s, duration = %s
                    WHERE id = %s
                """, (end_date, duration, cycle_record['id']))
            else:
                # Crear un nuevo registro
                cursor.execute("""
                    INSERT INTO cycle_records (start_date, end_date, duration)
                    VALUES (%s, %s, %s)
                """, (start_date, end_date, duration))
        
        # Paso 4: Verificar y corregir días faltantes
        today = date.today()
        start_date = period_records[0]['date']  # Primer día de período registrado
        
        # Obtener todas las fechas registradas
        cursor.execute("""
            SELECT date
            FROM temperatures
            WHERE date >= %s AND date <= %s
            ORDER BY date
        """, (start_date, today))
        
        date_records = cursor.fetchall()
        recorded_dates = [r['date'] for r in date_records]
        
        # Comprobar fechas faltantes entre el primer período y hoy
        missing_dates = []
        current_date = start_date
        while current_date <= today:
            if current_date not in recorded_dates:
                missing_dates.append(current_date)
            current_date += timedelta(days=1)
        
        if missing_dates:
            flash(f"Se detectaron {len(missing_dates)} fechas faltantes entre {start_date} y hoy.", "info")
        
        # Paso 5: Actualizar el contador de días actual
        last_period = period_records[-1]['date']
        days_since_period = (today - last_period).days + 1
        
        cursor.execute("""
            UPDATE cycle_counter
            SET day_counter = %s
        """, (days_since_period,))
        
        # Actualizar el contador local
        tracker.day_counter = days_since_period
        
        connection.commit()
        flash(f"Datos del ciclo corregidos: {records_updated} registros actualizados, {cycles_processed} ciclos procesados. Ciclo actual: Día {days_since_period}.", "success")
        
    except Exception as e:
        print(f"Error fixing cycle days: {e}")
        flash(f"Error al corregir los días del ciclo: {str(e)}", "danger")
        
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0') 