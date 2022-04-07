from flask import Blueprint, jsonify, request

from data.db_session import create_session
from data.__all_models import Jobs

blueprint = Blueprint(
    'jobs_api',
    __name__,
    template_folder='templates',
    static_folder='static')


@blueprint.route('/api/jobs')
def get_jobs():
    db_sess = create_session()
    jobs = db_sess.query(Jobs).all()
    return jsonify(
        {
            'jobs':
                [item.to_dict(only=('job', 'work_size', 'collaborators', 'is_finished', 'user.name'))
                 for item in jobs]
        }
    )


@blueprint.route('/api/jobs/<int:job_id>')
def get_one_jobs(job_id):
    db_sess = create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'job': job.to_dict(only=('job', 'work_size', 'collaborators', 'is_finished', 'user.name'))
        }
    )


@blueprint.route('/api/jobs', methods=['POST'])
def create_jobs():
    if not request.json:
        return jsonify({'error': 'Empty request'})

    elif not all(key in request.json for key in
                 ['team_leader', 'job', 'collaborators', 'is_finished', 'work_size']):
        return jsonify({'error': 'Bad request'})
    db_sess = create_session()
    job = Jobs()
    job.team_leader = request.json['team_leader']
    job.job = request.json['job']
    job.collaborators = request.json['collaborators']
    job.is_finished = request.json['is_finished']
    job.work_size = request.json['work_size']
    db_sess.add(job)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_jobs(job_id):
    db_sess = create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'Not found'})
    db_sess.delete(job)
    db_sess.commit()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:job_id>', methods=['PUT'])
def edit_jobs(job_id):
    db_sess = create_session()
    job = db_sess.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'Not found'})
    if not any(key in request.json for key in
               ['team_leader', 'job', 'collaborators', 'is_finished', 'work_size']):
        return jsonify({'error': 'Bad request'})
    job.team_leader = request.json.get('team_leader', job.team_leader)
    job.job = request.json.get('job', job.job)
    job.collaborators = request.json.get('collaborators', job.collaborators)
    job.is_finished = request.json.get('is_finished', job.is_finished)
    job.work_size = request.json.get('work_size', job.work_size)

    db_sess.commit()
    return jsonify({'success': 'OK'})
