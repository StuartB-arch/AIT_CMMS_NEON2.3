-- Fix the name for parts coordinator aspenson from 'April Penson' to 'Ashica Penson'
UPDATE users
SET full_name = 'Ashica Penson'
WHERE username = 'apenson';
