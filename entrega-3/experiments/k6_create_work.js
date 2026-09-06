import http from 'k6/http';
import { check } from 'k6';
export const options = {
  scenarios: {
    peak: {
      executor: 'constant-arrival-rate',
      rate: 500,
      timeUnit: '1s',
      duration: '5m',
      preAllocatedVUs: 200,
      maxVUs: 1000
    }
  },
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.01']
  }
};
export default function () {
  const payload = JSON.stringify({category:'plomeria',urgency:'alta',city:'Bogota',zone:'Norte'});
  const r = http.post('http://localhost:8000/works', payload,
    {headers:{'Content-Type':'application/json'}});
  check(r, {'created': x => x.status === 201});
}
