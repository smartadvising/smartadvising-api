// JavaScript Document
$(function () {
     Result();
        $("#advisor_college").change(function (e) {
            $("#advisor_department").empty();
           Result();
		   val= $(this).val();
		   var opt;
           
        //APPLIED STUDIES-1	   
		if(val == 1) {
	      opt = {
            ' All' : ' All' };
		}
		//ARTS & SCIENCES-2
		else if(val == 2) {
	      opt = {
			' All' : ' All',
            'Aerospace Studies' : 'Aerospace Studies',
            'Anthropology' : 'Anthropology',
		    'Biological Science' : 'Biological Science',
		    'Chemistry & Biochemistry' : 'Chemistry & Biochemistry',
			'Classics' : 'Classics',
			'Computational Science' : 'Computational Science', 
			'Computer Science' : 'Computer Science',
			'Earth, Ocean & Atmospheric Science' : 'Earth, Ocean & Atmospheric Science',
			'English' : 'English',
			'FSU-Teach' : 'FSU-Teach',
			'Geophysical Fluid Dynamics' : 'Geophysical Fluid Dynamics',
			'History' : 'History',
			'History & Philosophy of Science' : 'History & Philosophy of Science',
			'Humanities' : 'Humanities',
			'Mathematics' : 'Mathematics',
			'Middle Eastern Studies' : 'Middle Eastern Studies',
			'Military Science' : 'Military Science',
			'Modern Languages & Linguistics' : 'Modern Languages & Linguistics',
			'Molecular Biophysics' : 'Molecular Biophysics',
			'Philosophy' : 'Philosophy',
			'Physics' : 'Physics',
			'Psychology' : 'Psychology',
			'Religion' : 'Religion',
			'Science Teaching' : 'Science Teaching',
			'Scientific Computing' : 'Scientific Computing',
			'Statistics' : 'Statistics',
			'Women\'s Studies' : 'Women\'s Studies' };
	    }
		//BUSINESS-3
		else if(val == 3) {    
		  opt = {
			' All' : ' All',
            'Accounting' : 'Accounting',
			'Business Analytics, Information Systems & Supply Chain' :
			'Business Analytics, Information Systems & Supply Chain',
		    'Finance' : 'Finance',
		    'Management' : 'Management',
		    'Marketing' : 'Marketing',
			'Risk Management/ Insurance, Real Estate, & Legal Studies' : 
			'Risk Management/ Insurance, Real Estate, & Legal Studies' };
		}
		//COMMUNICATION AND INFORMATION-4
		else if(val == 4) {    
		  opt = {
			' All' : ' All',
            'School of Communication' : 'School of Communication',
            'School of Communication Science & Disorders' : 
			'School of Communication Science & Disorders',
		    'School of Information' : 'School of Information' };
		}
		//CRIMINOLOGY AND CRIMINAL JUSTICE-5
		else if(val == 5) {    
		  opt = {
		   ' All' : ' All',
            'Criminology & Criminal Justice' : 'Criminology & Criminal Justice',
            'Cyber Criminology' : 'Cyber Criminology' };
		}
		//EDUCATION-6
		else if(val == 6) {    
		  opt = {
			' All' : ' All',
            'Distance Learning' : 'Distance Learning',
            'Educational Leadership & Policy Studies' : 'Educational Leadership & Policy Studies',
		    'Educational Psychology & Learning Systems' : 'Educational Psychology & Learning Systems',
		    'Teacher Education' : 'Teacher Education',
		    'Sport Management' : 'Sport Management' };
		}
		//ENGINEERING
		else if(val == 7) {    
		  opt = {
			' All' : ' All',
            'Chemical & Biomedical Engineering' : 'Chemical & Biomedical Engineering',
            'Civil & Environmental Engineering' : 'Civil & Environmental Engineering',
		    'Electrical & Computer Engineering' : 'Electrical & Computer Engineering',
		    'Industrial Engineering' : 'Industrial Engineering',
		    'Mechanical Engineering' : 'Mechanical Engineering' };
		}
		//HUMAN SCIENCES
		else if(val == 8) {    
		  opt = {
			' All' : ' All',
            'Family & Child Sciences' : 'Family & Child Sciences',
            'Nutrition, Food & Exercise Sciences' : 'Nutrition, Food & Exercise Sciences',
		    'Retail Merchandising & Product Development' : 
			'Retail Merchandising & Product Development' };
		}
		//LAW
		else if(val == 9) {    
		  opt = {
            ' All' : ' All' };
		}
		//MEDICINE
		else if(val == 10) {    
		  opt = {
            ' All' : ' All' };
		}
		//MOTION PICTURE ARTS
		else if(val == 11) {    
		  opt = {
            ' All' : ' All' };
		}
		//MUSIC
		else if(val == 12) {    
		  opt = {
			' All' : ' All',
            'Arts Administration' : 'Arts Administration',
            'Bands' : 'Bands',
		    'Brass & Woodwinds' : 'Brass & Woodwinds',
		    'Choral' : 'Choral',
		    'Composition' : 'Composition',
			'Ethnomusicology/World Music' : 'Ethnomusicology/World Music',
			'Historical Musicology' : 'Historical Musicology',
			'Jazz Studies' : 'Jazz Studies',
            'Keyboard' : 'Keyboard',
		    'Music Education' : 'Music Education',
		    'Music Theatre' : 'Music Theatre',
		    'Music Therapy' : 'Music Therapy',
			'Music Theory' : 'Music Theory',
			'Opera Production' : 'Opera Production',
			'Percussion' : 'Percussion',
			'Strings/Orchestra' : 'Strings/Orchestra',
			'Voice' : 'Voice' };
		}
		//NURSING
		else if(val == 13) {    
		  opt = {
            ' All' : ' All' };
		}
		//SOCIAL SCIENCES AND PUBLIC POLICY
		else if(val == 14) {    
		  opt = {
			' All' : ' All',
            'Economics' : 'Economics',
			'Demography' : 'Demography',
            'Geography' : 'Geography',
		    'Political Science' : 'Political Science',
		    'Public Administration & Policy' : 'Public Administration & Policy',
		    'Sociology' : 'Sociology',
			'Urban & Regional Planning' : 'Urban & Regional Planning',
			'African American Studies' : 'African American Studies',
			'Asian Studies' : 'Asian Studies',
			'Environment and Society' : 'Environment and Society',
			'Health Policy Research' : 'Health Policy Research',
			'Interdisciplinary Social Science' : 'Interdisciplinary Social Science',
			'International Affairs' : 'International Affairs',
			'Latin American & Caribbean Studies' : 'Latin American & Caribbean Studies',
			'Public Health' : 'Public Health',
			'Russian & East European Studies' : 'Russian & East European Studies' };
		}
		//SOCIAL WORK
		else if(val == 15) {    
		  opt = {
            ' All' : ' All' };
		}
		//VISUAL ARTS, THEATRE AND DANCE
		else if(val == 16) {    
		  opt = {
			' All' : ' All',
            'Art' : 'Art',
            'Art Education' : 'Art Education',
		    'Art History' : 'Art History',
		    'Dance' : 'Dance',
		    'Interior Design' : 'Interior Design',
			'Theatre' : 'Theatre' };
		}
		//OTHER ADVISING SERVICES
		else if(val == 17) {    
		  opt = {
			' All' : ' All',
			'Academic Center for Excellence' : 'Academic Center for Excellence',
            'Career Center' : 'Career Center',
		    'Office of National Fellowships' : 'Office of National Fellowships',
			'Center for Academic Planning' : 'Center for Academic Planning',
			'Center for Academic Retention and Enhancement' : 'Center for Academic Retention and Enhancement',
			'Center for Exploratory Students' : 'Center for Exploratory Students',
		    'Center for Research & Academic Engagement' : 'Center for Research & Academic Engagement',
		    'Center for Leadership & Social Change' : 'Center for Leadership & Social Change',
			'Degree in Three' : 'Degree in Three',
			'FSU-Panama City, FL' : 'FSU-Panama City, FL',
			'Garnet & Gold' : 'Garnet & Gold',
			'Graduation Planning and Strategies Office' : 'Graduation Planning and Strategies Office',
			'International Programs' : 'International Programs',
			  'Prelaw' : 'Prelaw',
			  'Premed' : 'Premed',
			'Student Disability Resource Center' : 'Student Disability Resource Center',
			'Student Veterans Center' : 'Student Veterans Center',
			'Victim Advocate' : 'Victim Advocate',
			//'Athletics' : 'Athletics',
			'Honors' : 'Honors' };
		}
		
		// Entrepreneurship
		else if(val == 18) {    
		  opt = {
            ' All' : ' All' };
		}
		
		//Hospitality 
		else if(val == 19) {    
		  opt = {
            ' All' : ' All' };
		}
		
		  
	       $.each(opt, function(index, text) {
			   console.log("Index: " + index + 'text: ' + text);
        $("#advisor_department").append(
            $('<option></option>').val(text).html(text)
        );
      });
	});
  });
