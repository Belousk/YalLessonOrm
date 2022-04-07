from requests import get, post, delete, put

print(get('http://localhost:5000/api/v2/jobs/2').json())
print(get('http://localhost:5000/api/v2/jobs/666').json())
print(get('http://localhost:5000/api/v2/jobs/g').json())

print(post('http://localhost:5000/api/v2/jobs').json())  # Empty request

print(post('http://localhost:5000/api/v2/jobs',
           json={'job': 'Loh'}).json())  # Bad request

print(post('http://localhost:5000/api/v2/jobs',
           json={'job': 'Learn English', 'work_size': 10, 'collaborators': '1, 2, 3', 'is_finished': False,
                 'team_leader': 2}).json())  # Success request
print(delete('http://localhost:5000/api/v2/jobs/999').json())

print(delete('http://localhost:5000/api/v2/jobs/9').json())
# print(put('http://localhost:5000/api/v2/jobs/2', json={'job': 'S**k d**k'}))
