import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Jobsearch } from '../components/jobsearch/jobsearch';

@Injectable({
  providedIn: 'root',
})
export class JobsearchService {
  httpClient = inject(HttpClient)
  getJobSearch(){
    return this.httpClient.get<Jobsearch[]>('http://127.0.0.1:8000/jobs/')
  }
}
