from flask import render_template, Blueprint, abort
from consultas import consulta


proyectos_bp = Blueprint('proyectos', __name__)


@proyectos_bp.route('/proyectos')
def listado():
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

    return render_template(
        'proyectos.html',
        proyectos=proyectos_lista
    )


@proyectos_bp.route('/proyecto/<int:id>')
def detalle(id):
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
        WHERE p.id_proyectos = %s
          AND p.activo = 1
    """

    resultado = consulta(query, (id,))

    if not resultado:
        abort(404)

    proyecto_data = resultado[0]

    galeria = consulta("""
        SELECT
            id_galeria,
            url_imagen,
            descripcion,
            orden
        FROM proyecto_galeria
        WHERE id_proyecto = %s
        ORDER BY orden ASC, id_galeria ASC
    """, (id,))

    videos = consulta("""
        SELECT
            id_video,
            url_video,
            titulo,
            orden
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
        WHERE pa.id_proyecto = %s
          AND a.activo = 1
        ORDER BY a.apellidos ASC, a.nombres ASC
    """, (id,))

    return render_template(
        'proyecto.html',
        proyecto=proyecto_data,
        galeria=galeria,
        videos=videos,
        aprendices=aprendices
    )
