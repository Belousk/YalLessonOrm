from flask_restful import reqparse, abort, Resource

from flask import jsonify
from data.__all_models import Jobs
from data.db_session import create_session

parser = reqparse.RequestParser()
parser.add_argument('team_leader', required=True, type=int)
parser.add_argument('job', required=True)
parser.add_argument('work_size', required=True, type=int)
parser.add_argument('collaborators', required=True)
parser.add_argument('is_finished', required=True, type=bool)


def abort_if_job_not_found(job_id):
    session = create_session()
    job = session.query(Jobs).get(job_id)
    if not job:
        abort(404, message=f"Jobs {job_id} not found")


class JobsResource(Resource):
    def get(self, job_id):
        abort_if_job_not_found(job_id)
        session = create_session()
        job = session.query(Jobs).get(job_id)
        return jsonify({'jobs': job.to_dict(
            only=('job', 'work_size', 'collaborators', 'is_finished', 'user.name'))})

    def delete(self, job_id):
        abort_if_job_not_found(job_id)
        session = create_session()
        job = session.query(Jobs).get(job_id)
        session.delete(job)
        session.commit()
        return jsonify({'success': 'OK'})


class JobsListResource(Resource):
    def get(self):
        session = create_session()
        job = session.query(Jobs).all()
        return jsonify({'job': [item.to_dict(
            only=('job', 'work_size', 'collaborators', 'is_finished', 'user.name')) for item in job]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        job = Jobs()
        print(args['job'])
        job.team_leader = args['team_leader']
        job.job = args['job']
        job.work_size = args['work_size']
        job.collaborators = args['collaborators']
        job.is_finished = args['is_finished']
        session.add(job)
        session.commit()
        return jsonify({'args': args['job'], 'success': 'OK'})
