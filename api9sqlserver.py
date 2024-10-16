from flask import Flask, jsonify, request
import pyodbc
from datetime import datetime
import traceback

app = Flask(__name__)

def get_db_connection():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-KJ188GQ\\SQLEXPRESS;"
            "DATABASE=NovaAkademi;"
            "Trusted_Connection=yes;"
        )
        return conn
    except pyodbc.Error as e:
        print(f"Veritabanı bağlantı hatası: {e}")
        return None

@app.route("/add-book", methods=["POST"])
def post_book():
    conn = get_db_connection()  # Parantez ekleyin
    if conn is None:
        return jsonify({"error": "Veritabanına bağlantı bulunamadı."}), 500
    try:
        data = request.json
        print(f"Alınan veri: {data}")

        yazar_id = data.get("YazarID")
        baslik = data.get("Başlık")
        yayin_yili_str = data.get("YayınYılı")

        if yazar_id is None or baslik is None or yayin_yili_str is None:
            return jsonify({"error": "Eksik veri: YazarID, Başlık ve YayınYılı gerekli."}), 400
        try:
            yayin_yili = datetime.strptime(yayin_yili_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "YayınYılı geçersiz formatta. Format YYYY-MM-DD."}), 400
        
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dbo.Kitaplar (YazarID, Başlık, YayınYılı) VALUES (?, ?, ?)",
            (yazar_id, baslik, yayin_yili)
        )

        conn.commit()
        return jsonify({"message": "Kitap başarıyla eklendi."}), 201
    except pyodbc.Error as e:
        print("Hata:", e)
        return jsonify({"error": f"Veritabanı hatası: {e}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/book/del/<int:yazar_id>', methods=["DELETE"])
def user_delete(yazar_id):
    conn = get_db_connection()  # Parantez ekleyin
    if conn is None:
        return jsonify({"error": "Veritabanına bağlanılamadı."}), 500
    
    try: 
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM dbo.Kitaplar WHERE YazarID= ?",
            (yazar_id)
        )
        if cursor.rowcount == 0:
            return jsonify({"error": "Belirtilen kitap bulunamadı."}), 404
        conn.commit()
        return jsonify({"message": "Kitap başarıyla silindi."}), 200
    
    except Exception as e:
        print("Hata:", e)
        print("Traceback:", traceback.format_exc())
        return jsonify({"error": f"Veritabanı hatası: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

@app.route('/book-update', methods=["PUT"])
def book_update():
    conn = get_db_connection()  # Parantez ekleyin
    if conn is None:
        return jsonify({"error": "Veritabanına bağlanılamadı."}), 500
    
    try:
        data = request.json
        print(f"Alınan veri: {data}")
        yazar_id = data.get("YazarID")
        baslik = data.get("Başlık")
        yayin_yili_str = data.get("YayınYılı")

        if yazar_id is None or baslik is None or yayin_yili_str is None:
            return jsonify({"error": "Eksik veri: YazarID, Başlık ve YayınYılı gerekli."}), 400
        
        try:
            yayin_yili = datetime.strptime(yayin_yili_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "YayınYılı geçersiz formatta. Format: YYYY-MM-DD."}), 400
        
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE dbo.Kitaplar SET Başlık=?, YayınYılı=? WHERE YazarID=?",
            (baslik, yayin_yili,yazar_id)  # yayin_yili_str yerine yayin_yili kullanın
        )

        conn.commit()
        return jsonify({"message": "Kitap başarıyla güncellendi."}), 200
    except Exception as e:
        print("Hata:", e)
        print("Traceback:", traceback.format_exc())
        return jsonify({"error": f"Veritabanı hatası: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
