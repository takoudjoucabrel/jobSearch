import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { JobsearchList } from './components/jobsearch-list/jobsearch-list';

@Component({
  selector: 'app-root',
  imports: [JobsearchList],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('jobSearch');
}
