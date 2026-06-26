import { Routes } from '@angular/router';
import { Jobsearch } from './components/jobsearch/jobsearch';
import { Title } from '@angular/platform-browser';
import { JobsearchList } from './components/jobsearch-list/jobsearch-list';
import { App } from './app';

export const routes: Routes = [
  { path: '', component: App },
  { path: 'jobsearch/:id', component: Jobsearch },
  
];
