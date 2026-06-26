import { Jobsearch } from '../jobsearch/jobsearch';
import { Component } from '@angular/core';
import { JobSearch , MOCK_JOBS, MOCK_COMPANIES } from './../../modele/jobsearch';

@Component({
  selector: 'app-jobsearch-list',
  imports: [Jobsearch],
  templateUrl: './jobsearch-list.html',
  styleUrl: './jobsearch-list.css',
})
export class JobsearchList {
  jobsearchs: JobSearch[];
  constructor() {
    this.jobsearchs = MOCK_JOBS;
    for (let index = 0; index < this.jobsearchs.length; index++) {
      this.jobsearchs[index].company = MOCK_COMPANIES[index]
    } 
  }
}
