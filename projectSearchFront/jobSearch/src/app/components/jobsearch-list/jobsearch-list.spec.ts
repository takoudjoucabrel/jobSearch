import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JobsearchList } from './jobsearch-list';

describe('JobsearchList', () => {
  let component: JobsearchList;
  let fixture: ComponentFixture<JobsearchList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JobsearchList],
    }).compileComponents();

    fixture = TestBed.createComponent(JobsearchList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
