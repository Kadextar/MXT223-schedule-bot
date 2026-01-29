
def get_exams():
    """Get all exams sorted by date"""
    sql = "SELECT * FROM exams ORDER BY exam_date ASC"
    is_postgres = bool(DATABASE_URL)
    if is_postgres:
        sql = sql.replace('?', '%s')
    
    results = execute_query(sql, fetch_one=False)
    if not results:
        return []
    
    exams = []
    for row in results:
        exams.append({
            'id': row[0],
            'subject': row[1],
            'teacher': row[2],
            'exam_date': str(row[3]),
            'exam_time': row[4],
            'room': row[5],
            'exam_type': row[6],
            'notes': row[7]
        })
    return exams
