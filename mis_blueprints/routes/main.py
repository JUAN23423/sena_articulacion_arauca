from flask import render_template, session, url_for, redirect, flash, request, Blueprint, abort
from consultas import consulta, insertar


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def inicio():
    query1 = """
        SELECT
            p.id_proyectos AS id,
            p.nombre,
            p.descripcion_corta AS descripcion,
            p.foto_principal AS foto,
            t.nombre AS tecnico,
            c.nombre AS colegio,
            m.nombre AS municipio
        FROM proyectos p
        INNER JOIN tecnicos t ON t.id_tecnicos = p.id_tecnico
        INNER JOIN colegios c ON c.id_colegios = t.id_colegio
        INNER JOIN municipios m ON m.id_municipios = c.id_municipios
        WHERE p.activo = 1
        ORDER BY p.nombre ASC
    """
    query2 = "SELECT id_colegios AS id, nombre, slogan, logo FROM colegios"
    query3 = "SELECT id_municipios AS id, nombre, foto FROM municipios"
    query4 = "SELECT id_instructor AS id, nombres, apellidos, id_profesion, foto FROM instructor"

    proyectos = consulta(query1)
    colegios = consulta(query2)
    municipios = consulta(query3)
    instructores = consulta(query4)

    return render_template(
        'index.html',
        proyectos=proyectos,
        colegios=colegios,
        municipios=municipios,
        instructores=instructores
    )


@main_bp.route('/proyectos')
def proyectos():
    query = """
        SELECT
            p.id_proyectos AS id,
            p.nombre,
            p.descripcion_corta,
            p.foto_principal,
            p.fecha_inicio,
            p.fecha_fin,
            t.ficha,
            t.nombre AS tecnico,
            c.nombre AS colegio,
            m.nombre AS municipio
        FROM proyectos p
        INNER JOIN tecnicos t ON t.id_tecnicos = p.id_tecnico
        INNER JOIN colegios c ON c.id_colegios = t.id_colegio
        INNER JOIN municipios m ON m.id_municipios = c.id_municipios
        WHERE p.activo = 1
        ORDER BY p.nombre ASC
    """
    proyectos_lista = consulta(query)
    return render_template('proyectos.html', proyectos=proyectos_lista)


@main_bp.route('/proyecto/<int:id>')
def proyecto(id):
    query = """
        SELECT
            p.*,
            t.ficha,
            t.nombre AS tecnico_nombre,
            t.foto_principal AS tecnico_foto,
            c.id_colegios,
            c.nombre AS colegio_nombre,
            c.slogan AS colegio_slogan,
            c.logo AS colegio_logo,
            m.id_municipios,
            m.nombre AS municipio_nombre,
            mo.nombre AS modalidad_nombre,
            i.nombres AS instructor_nombres,
            i.apellidos AS instructor_apellidos,
            i.foto AS instructor_foto,
            i.perfi_profesional AS instructor_perfil
        FROM proyectos p
        INNER JOIN tecnicos t ON t.id_tecnicos = p.id_tecnico
        INNER JOIN colegios c ON c.id_colegios = t.id_colegio
        INNER JOIN municipios m ON m.id_municipios = c.id_municipios
        INNER JOIN modalidad mo ON mo.id_modalidad = t.id_modalidad
        LEFT JOIN instructor i ON i.id_instructor = t.id_instructor
        WHERE p.id_proyectos = %s AND p.activo = 1
    """
    resultado = consulta(query, (id,))

    if not resultado:
        abort(404)

    proyecto_data = resultado[0]

    galeria = consulta("""
        SELECT id_galeria, url_imagen, descripcion, orden
        FROM proyecto_galeria
        WHERE id_proyecto = %s
        ORDER BY orden ASC, id_galeria ASC
    """, (id,))

    videos = consulta("""
        SELECT id_video, url_video, titulo, orden
        FROM proyecto_videos
        WHERE id_proyecto = %s
        ORDER BY orden ASC, id_video ASC
    """, (id,))

    aprendices = consulta("""
        SELECT
            a.id_aprendices,
            a.nombres,
            a.apellidos,
            a.foto
        FROM proyecto_aprendices pa
        INNER JOIN aprendices a ON a.id_aprendices = pa.id_aprendiz
        WHERE pa.id_proyecto = %s AND a.activo = 1
        ORDER BY a.apellidos ASC, a.nombres ASC
    """, (id,))

    return render_template(
        'proyecto_detalle.html',
        proyecto=proyecto_data,
        galeria=galeria,
        videos=videos,
        aprendices=aprendices
    )


@main_bp.route('/municipio/<int:id>')
def municipio(id):
    query = "SELECT * FROM municipios WHERE id_municipios = %s"
    municipio_data = consulta(query, (id,))
    return render_template('municipios.html', municipio=municipio_data)


@main_bp.route('/colegios')
def colegios():
    query = '''
        SELECT
            c.id_colegios AS id,
            c.nombre AS colegio,
            c.logo AS logo,
            m.nombre AS municipio
        FROM colegios c
        INNER JOIN municipios m ON m.id_municipios = c.id_municipios
    '''
    colegios_lista = consulta(query)
    return render_template('colegios.html', colegios=colegios_lista)


@main_bp.route('/colegio/<id>')
def colegio(id):
    query = 'SELECT * FROM colegios WHERE id_colegios = %s'
    colegio_data = consulta(query, (id,))

    if not colegio_data:
        abort(404)

    return render_template('colegio.html', colegio=colegio_data[0])


@main_bp.route('/instructor/<int:id>')
def instructor(id):
    query = 'SELECT * FROM instructor WHERE id_instructor = %s'
    instructor_data = consulta(query, (id,))

    if not instructor_data:
        abort(404)

    return render_template('instructor.html', instructor=instructor_data[0])
