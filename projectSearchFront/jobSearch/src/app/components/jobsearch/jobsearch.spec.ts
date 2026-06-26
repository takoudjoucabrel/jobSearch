import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Jobsearch } from './jobsearch';

describe('Jobsearch', () => {
  let component: Jobsearch;
  let fixture: ComponentFixture<Jobsearch>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Jobsearch],
    }).compileComponents();

    fixture = TestBed.createComponent(Jobsearch);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
