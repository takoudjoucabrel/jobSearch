import { TestBed } from '@angular/core/testing';

import { JobsearchService } from './jobsearch-service';

describe('JobsearchService', () => {
  let service: JobsearchService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(JobsearchService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
