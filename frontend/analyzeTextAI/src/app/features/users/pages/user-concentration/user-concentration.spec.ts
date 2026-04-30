import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserConcentration } from './user-concentration';

describe('UserConcentration', () => {
  let component: UserConcentration;
  let fixture: ComponentFixture<UserConcentration>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserConcentration]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserConcentration);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
