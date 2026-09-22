const GRADE_BANDS=[[90,'A+',4.0],[80,'A',3.7],[70,'B',3.3],[60,'C',3.0],[50,'D',2.0],[40,'E',1.0],[0,'F',0.0]];
function calculateGrade(marks,total){if(Number(total)<=0)return {grade:'N/A',gpa_points:0};const pct=(Number(marks)/Number(total))*100;for(const [min,grade,gpa_points] of GRADE_BANDS)if(pct>=min)return {grade,gpa_points};return {grade:'F',gpa_points:0};}
module.exports={GRADE_BANDS,calculateGrade};
