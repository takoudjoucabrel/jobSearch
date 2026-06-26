import { JobSearch } from './../../modele/jobsearch';
import { Component, input } from '@angular/core';

@Component({
  selector: 'app-jobsearch',
  imports: [],
  templateUrl: './jobsearch.html',
  styleUrl: './jobsearch.css',
})
export class Jobsearch {
jobsearch = input.required<JobSearch>()

}
