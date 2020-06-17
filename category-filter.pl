#!/usr/bin/perl -w

#
# The categories recognized by tvheadend (see epg.c) 
#  

my $MOVIE             =    "Drama";
my $THRILLER          =    "Thriller";
my $ADVENTURE         =    "Adventure";
my $SF                =    "Science fiction";
my $COMEDY            =    "Comedy";
my $SOAP              =    "Soap";
my $ROMANCE           =    "Romance";
my $HISTORICAL        =    "History";
my $XXX               =    "Adult movie";

my $NEWS              =    "News";
my $WEATHER           =    "Weather";
my $NEWS_MAGAZINE     =    "News magazine";
my $DOCUMENTARY       =    "Documentary";
my $DEBATE            =    "Interview";
my $INTERVIEW         =    $DEBATE ;

my $SHOW              =    "Show";
my $GAME              =    "Game show";
my $VARIETY           =    "Variety";
my $TALKSHOW          =    "Talk show";

my $SPORT             =    "Sports";
my $SPORT_SPECIAL     =    "Sports";
my $SPORT_MAGAZINE    =    "Sports magazines";
my $FOOTBALL          =    "Football";
my $TENNIS            =    "Tennis";
my $SPORT_TEAM        =    "Team sports (excluding football)";
my $ATHLETICS         =    "Athletics";
my $SPORT_MOTOR       =    "Motor sport";
my $SPORT_WATER       =    "Water sport";

my $KIDS              =    "Children";
my $KIDS_0_5          =    "Children";
my $KIDS_6_14         =    "Children";
my $KIDS_10_16        =    "Children";
my $EDUCATIONAL       =    "Educational";
my $CARTOON           =    "Cartoon";

my $MUSIC             =    "Music";
my $ROCK_POP          =    "Rock / Pop";
my $CLASSICAL         =    "Classical";
my $FOLK              =    "Folk";
my $JAZZ              =    "Jazz";
my $OPERA             =    "Musical";

my $CULTURE           =    "Culture";
my $PERFORMING        =    "Performing arts";
my $FINE_ARTS         =    "Fine arts";
my $RELIGION          =    "Religion";
my $POPULAR_ART       =    "Arts";
my $LITERATURE        =    "Literature";
my $FILM              =    "Cinema";
my $EXPERIMENTAL_FILM =    "Experimental film / Video";
my $BROADCASTING      =    "Press";

my $SOCIAL            =    "Political";
my $MAGAZINE          =    "Magazine";
my $ECONOMIC          =    "Economics";
my $VIP               =    "Remarkable people";

my $SCIENCE           =    "Science";
my $NATURE            =    "Nature";
my $TECHNOLOGY        =    "Science";
my $DIOLOGY           =    $TECHNOLOGY;
my $MEDECINE          =    "Medical";
my $FOREIGN           =    "Documentary";
my $SPIRITUAL         =    "Religious";
my $FURTHER_EDUCATION =    "Further education";
my $LANGUAGES         =    "Languages";

my $HOBBIES           =    "Leisure hobbies";
my $TRAVEL            =    "Travel";
my $HANDICRAF         =    "Handicraft";
my $MOTORING          =    "Motoring";
my $FITNESS           =    "Fitness health";
my $COOKING           =    "Cooking";
my $SHOPPING          =    "Shopping";
my $GARDENING         =    "Gardening";

#
# This is the 
#
#
#

my %REPLACE=(

    "Fitness"           => $FITNESS ,
	"Esportivo"          => $SPORT ,
    "Futebol"            => $FOOTBALL ,
	"Futebol de Salão"   => $FOOTBALL ,
    "Basquete"           => $SPORT ,
	"Vôlei"              => $SPORT ,
    "Luta"               => $SPORT ,
    "Futebol Feminino"   => $FOOTBALL ,
	"Beisebol"           => $SPORT ,
	"Atletismo"          => $SPORT ,
	"Tênis"              => $SPORT ,
	"Boxe"               => $SPORT ,
	"Rugby"              => $SPORT ,
	"Automobilismo"      => $SPORT_MOTOR ,
	"Debate / Esportivo" => $SPORT ,
	"Surfe"              => $SPORT ,
    "Radical"            => $SPORT ,
	"Sports"             => $SPORT ,
    "Ciclismo"           => $SPORT ,
    "Tiercé"             => $SPORT ,
	"Jeu"                => $GAME ,	
	"Erótico"            => $XXX ,
	"Político"           => $NEWS ,
	"Política"           => $NEWS ,
    "Informativo"        => $NEWS ,
	"Jornalismo"         => $NEWS ,
    "Jornalismo/Informativo" => $NEWS ,
	"Variedades/Entrevista" => $DEBATE ,
	"Variedades/Debate"  => $DEBATE ,
	"Débat"              => $DEBATE ,
	"Debate"             => $DEBATE ,
	"Entrevista"         => $TALKSHOW ,
	"Talk Show"          => $TALKSHOW ,
	"Interview"          => $INTERVIEW ,
	"Meteorologia"       => $WEATHER ,
	"Emission politique" => $SOCIAL,
    "Politique"          => $SOCIAL ,
	"Comunicação"        => $BROADCASTING ,
    "Variedades/Religião"=> $RELIGION ,
	"Séries/Religião"    => $RELIGION ,
	"Religião"           => $RELIGION ,
	"Medicina"           => $MEDECINE ,
    "Saúde"              => $MEDECINE ,
	"Sobrenatural"       => $SPIRITUAL ,
	"Animação"           => $CARTOON ,
	"Desenho"            => $CARTOON ,
	"Anime"              => $CARTOON ,
	"Infantil"           => $KIDS ,
	"Juvenil"            => $KIDS ,
	"Educativo"          => $EDUCATIONAL ,
	"Documentário"       => $DOCUMENTARY ,
	"Investigação"       => $DOCUMENTARY ,
	"Biografia"          => $DOCUMENTARY ,
	"Séries/Documentário" => $DOCUMENTARY ,
	"Épico"              => $DOCUMENTARY ,
	"Histórico"          => $HISTORICAL ,
	"Histórica"          => $HISTORICAL ,
	"Pesca"              => $NATURE,
	"Meio Ambiente"      => $NATURE ,
	"Ecologia"           => $NATURE ,
	"Cultural"           => $CULTURE ,
	"Variedades/Cultural" => $CULTURE ,
	"Séries/Cultural"    => $CULTURE ,
	"Musical"            => $MUSIC ,
	"Show"               => $MUSIC ,
	"Clip"               => $MUSIC ,
	"Variedades/Musical" => $MUSIC ,
	"Musique"            => $MUSIC ,
	"Dança"              => $PERFORMING ,
    "Artes"              => $PERFORMING ,
    "Balé"               => $PERFORMING ,
    "Teatro"             => $PERFORMING ,
	"Variedades/Artes"   => $PERFORMING ,
	"Spectacle"          => $PERFORMING ,
	"Ópera"              => $MUSIC ,
	"Comportamento"      => $VARIETY ,
	"Moda"               => $VARIETY ,
	"Moda e Estilo"      => $VARIETY ,
	"Programa"           => $VARIETY ,
	"Variedades/Diversos" => $VARIETY ,
	"Diversos"           => $VARIETY ,
	"Divertissement"     => $VARIETY ,
	"Télé-réalité"       => $VARIETY ,    
    "Divers"             => $VARIETY ,
    "Reality Show"       => $VARIETY ,        
    "Divers"             => $VARIETY ,
	"Série"              => $VARIETY  , 
	"Culinária"          => $COOKING ,
	"Magazine"           => $MAGAZINE ,
	"Revista Feminina"   => $MAGAZINE ,
	"Especial"           => $MAGAZINE,
	"Novela"             => $SOAP ,
	"Feuilleton"         => $SOAP ,
	"Viagem"             => $TRAVEL ,
	"Turismo"         	 => $TRAVEL ,
	"Televendas"         => $SHOPPING ,
	"Competição"         => $GAME ,
	"Game Show"          => $GAME ,
	"Suspense"           => $THRILLER ,
    "Terror"             => $THRILLER ,
	"Policial"           => $THRILLER ,
	"Ação"               => $ADVENTURE ,
	"Aventura"           => $ADVENTURE ,
	"Western"            => $ADVENTURE ,
	"Guerra"             => $ADVENTURE ,
	"Drama"              => $MOVIE ,
    "Cinema"             => $MOVIE ,
	"Téléfilm"           => $MOVIE ,
	"Romance"            => $ROMANCE ,
	"Humor"              => $COMEDY ,
	"Comédia"            => $COMEDY ,
    "Ficção"             => $SF ,
    "Ciência"            => $SCIENCE ,
	"Émission"           => 0,    
    "Fin"                => 0,
    "Fin des programmes" => 0 ,	
	"Loterie"            => 0 ,
) ; 

my $PRE  = '<category lang=\"pt\">' ;
my $POST = '</category>'  ;

sub myfilter {
	my ($a) = @_;
	if ( exists $REPLACE{$a} ) {     
		return $REPLACE{$a} ;
	} else {
		print STDERR "Warning: Unmanaged category: '$a'\n" ;
		return $a ;
	}
}

while (<>) {
    my $line = $_ ;
    $line =~ s/($PRE)(.*)($POST)/"$1".myfilter("$2")."$3"/ge ;
    print $line;
}
    