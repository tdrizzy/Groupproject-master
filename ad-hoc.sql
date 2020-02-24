select u.id, u.username, u.first_name, u.last_name, t.id, s.name, p.title
from   users u left join team_member m on u.id = m.user_id
       left join team t on m.team_id = t.id
       left join project p on t.project_id = p.id
       left join status s on s.id = t.status_id
where  not exists (select 1
                   from   team_member m join team t on t.id = m.team_id
                                        join status s on s.id = t.status_id
                   where  s.name not in ('Declined'))
                   and    m.user_id = u.id
and    u.is_student = 1
order by 7


select p.id, p.title, concat(u.first_name, ' ',u.last_name) as PM
from   project p join team t on t.project_id = p.id
       join status s on s.id = t.status_id
       join    team_member m on t.id = m.team_id
       join    users u on u.id = m.user_id
where  m.project_manager = 1
and    s.name = 'Accepted'


select u.id, u.username, u.first_name, u.last_name, t.id, s.name, p.title, s.name
from   users u left join team_member m on u.id = m.user_id
       left join team t on m.team_id = t.id
       left join project p on t.project_id = p.id
       left join status s on s.id = t.status_id
where    u.is_student = 1
and    s.name not in ('Accepted', 'Declined')
order by 7


select u.id, u.username, u.first_name, u.last_name
from   users u left join team_member m on u.id = m.user_id
where  u.is_student = 1
and    not exists (
  select 1
  from   team_member m
  where  m.user_id = u.id
)


select t.id, p.title, u.username, u.first_name, u.last_name, m.project_manager
from   project p join team t on t.project_id = p.id
       join team_member m on t.id = m.team_id
       join users u on m.user_id = u.id
       join status s on s.id = t.status_id
where  s.name in ('Accepted', 'Shortlisted')
