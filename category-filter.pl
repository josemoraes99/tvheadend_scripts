#!/usr/bin/perl -w

#
# The categories recognized by tvheadend (see epg.c) 
#  

my $MOVIE             =    "Movie / Drama";
my $THRILLER          =    "Detective / Thriller";
my $ADVENTURE         =    "Adventure / Western / War";
my $SF                =    "Science fiction / Fantasy / Horror";
my $COMEDY            =    "Comedy";
my $SOAP              =    "Soap / Melodrama / Folkloric";
my $ROMANCE           =    "Romance";
my $HISTORICAL        =    "Serious / Classical / Religious / Historical movie / Drama";
my $XXX               =    "Adult movie / Drama";

my $NEWS              =    "News / Current affairs";
my $WEATHER           =    "News / Weather report";
my $NEWS_MAGAZINE     =    "News magazine";
my $DOCUMENTARY       =    "Documentary";
my $DEBATE            =    "Discussion / Interview / Debate";
my $INTERVIEW         =    $DEBATE ;

my $SHOW              =    "Show / Game show";
my $GAME              =    "Game show / Quiz / Contest";
my $VARIETY           =    "Variety show";
my $TALKSHOW          =    "Talk show";

my $SPORT             =    "Sports";
my $SPORT_SPECIAL     =    "Special events (Olympic Games; World Cup; etc.)";
my $SPORT_MAGAZINE    =    "Sports magazines";
my $FOOTBALL          =    "Football / Soccer";
my $TENNIS            =    "Tennis / Squash";
my $SPORT_TEAM        =    "Team sports (excluding football)";
my $ATHLETICS         =    "Athletics";
my $SPORT_MOTOR       =    "Motor sport";
my $SPORT_WATER       =    "Water sport";

my $KIDS              =    "Children's / Youth programmes";
my $KIDS_0_5          =    "Pre-school children's programmes";
my $KIDS_6_14         =    "Entertainment programmes for 6 to 14";
my $KIDS_10_16        =    "Entertainment programmes for 10 to 16";
my $EDUCATIONAL       =    "Informational / Educational / School programmes";
my $CARTOON           =    "Cartoons / Puppets";

my $MUSIC             =    "Music / Ballet / Dance";
my $ROCK_POP          =    "Rock / Pop";
my $CLASSICAL         =    "Serious music / Classical music";
my $FOLK              =    "Folk / Traditional music";
my $JAZZ              =    "Jazz";
my $OPERA             =    "Musical / Opera";

my $CULTURE           =    "Arts / Culture (without music)";
my $PERFORMING        =    "Performing arts";
my $FINE_ARTS         =    "Fine arts";
my $RELIGION          =    "Religion";
my $POPULAR_ART       =    "Popular culture / Traditional arts";
my $LITERATURE        =    "Literature";
my $FILM              =    "Film / Cinema";
my $EXPERIMENTAL_FILM =    "Experimental film / Video";
my $BROADCASTING      =    "Broadcasting / Press";

my $SOCIAL            =    "Social / Political issues / Economics";
my $MAGAZINE          =    "Magazines / Reports / Documentary";
my $ECONOMIC          =    "Economics / Social advisory";
my $VIP               =    "Remarkable people";

my $SCIENCE           =    "Education / Science / Factual topics";
my $NATURE            =    "Nature / Animals / Environment";
my $TECHNOLOGY        =    "Technology / Natural sciences";
my $DIOLOGY           =    $TECHNOLOGY;
my $MEDECINE          =    "Medicine / Physiology / Psychology";
my $FOREIGN           =    "Foreign countries / Expeditions";
my $SPIRITUAL         =    "Social / Spiritual sciences";
my $FURTHER_EDUCATION =    "Further education";
my $LANGUAGES         =    "Languages";

my $HOBBIES           =    "Leisure hobbies";
my $TRAVEL            =    "Tourism / Travel";
my $HANDICRAF         =    "Handicraft";
my $MOTORING          =    "Motoring";
my $FITNESS           =    "Fitness and health";
my $COOKING           =    "Cooking";
my $SHOPPING          =    "Advertisement / Shopping";
my $GARDENING         =    "Gardening";

#
# This is the 
#
#
#

my %REPLACE=(
    "Ação"               => $ADVENTURE ,
    "Drama"              => $MOVIE ,
    "Comédia"            => $COMEDY ,
    "Ficção"             => $SF ,
    "Policial"           => $THRILLER ,
    "Romance"            => $ROMANCE ,
    "Suspense"           => $THRILLER ,
    "Terror"             => $THRILLER ,
    "Aventura"           => $ADVENTURE ,
    "Pesca"              => $NATURE,
    "Musical"            => $MUSIC ,
    "Documentário"       => $DOCUMENTARY ,
    "Débat"              => $SOCIAL ,
    "Animação"           => $CARTOON ,
    "Educativo"          => $EDUCATIONAL ,
    "Show"               => $MUSIC ,
    "Viagem"             => $TRAVEL ,
    "Erótico"            => $XXX ,
    "Meio Ambiente"      => $NATURE ,
    "Cultural"           => $CULTURE ,
    "Meteorologia"       => $WEATHER ,
    "Saúde"              => $MEDECINE ,
    "Ciência"            => $SCIENCE ,
    "Culinária"          => $COOKING ,
    "Comportamento"      => $VARIETY ,
    "Debate"             => $DEBATE ,
    "Game Show"          => $GAME ,
    "Político"           => $NEWS ,
    "Cinema"             => $MOVIE ,
    "Moda e Estilo"      => $VARIETY ,
    "Ecologia"           => $NATURE ,
    "Western"            => $ADVENTURE ,
    "Sobrenatural"       => $SPIRITUAL ,
    "Biografia"          => $DOCUMENTARY ,
    "Histórico"          => $HISTORICAL ,
    "A Terra está em perigo"      => $DOCUMENTARY ,
    "Televendas"         => $SHOPPING ,
    "Investigação"       => $DOCUMENTARY ,
    "Talk Show"          => $TALKSHOW ,
    "Épico"              => $DOCUMENTARY ,
    "Juvenil"            => $KIDS_10_16 ,
    "Programa"           => $VARIETY ,
    "Teatro"             => $PERFORMING ,
    "Histórica"          => $HISTORICAL ,
    "Guerra"             => $ADVENTURE ,
    "Atletismo"          => $ATHLETICS ,
    "Automobilismo"      => $SPORT_MOTOR ,
    "Desenho"            => $CARTOON ,
    "Surfe"              => $SPORT_WATER ,
    "Radical"            => $SPORT ,
    "Dança"              => $PERFORMING ,
    "Artes"              => $PERFORMING ,
    "Balé"               => $PERFORMING ,
    "Ópera"              => $OPERA ,
    "Competição"         => $GAME ,
    "Medicina"           => $MEDECINE ,
    "Comunicação"        => $BROADCASTING ,
    "Turismo"         => $TRAVEL ,
    
    "Animação De Jennifer Coyle"                                                      => 0 ,
    "Musical De Bernardo Mendonça"                                                      => 0 ,
    "Mulher, socialista convicta, entra em coma e desperta 8 meses depois"                                                      => 0 ,
    "Alex é um engenheiro cibernético"                                                      => 0 ,
    "Musical De Gabriela Figueiredo"                                                      => 0 ,
    
    
    "A França está sob ocupação"                                                      => 0 ,
    "Comédia De Tim Heidecker"                                                      =>$COMEDY ,
    "A séries conta a história de duas famílias, os Canon e os Montoya, donos de grandes áreas do Arizona"            => 0 ,
    "Drew é um garoto tímido da cidade e Sherrie uma garota do interior"            => 0 ,
    "O irmão de Rich quer uma Smith &amp; Wesson 686 Plus personalizada"            => 0 ,
    
    "Divertissement"     => $VARIETY ,
    "Novela"             => $SOAP ,
    "Émission"           => 0,
    "Feuilleton"         => $SOAP ,
    "Fin"                => 0,
    "Fin des programmes" => 0 ,
    "Interview"          => $INTERVIEW ,
    "Jeu"                => $GAME ,
    "Infantil"           => $KIDS ,
    "Informativo"        => $NEWS ,
    "Loterie"            => 0 ,
    "Magazine"           => $MAGAZINE ,
    "Opéra"              => $OPERA ,
    "Série"              => $MOVIE  ,
    "Spectacle"          => $PERFORMING ,
    
    "Esportivo"          => $SPORT ,
    "Futebol"            => $FOOTBALL ,
    "Basquete"           => $SPORT ,
    "Luta"               => $SPORT ,
    "Futebol Feminino"   => $FOOTBALL ,
    
    "Entrevista"          => $TALKSHOW ,
    "Téléfilm"           => $MOVIE ,
    "Télé-réalité"       => $VARIETY ,
    "Diversos"         => $VARIETY ,
    "Tiercé"             => $SPORT ,
    "Divers"             => $VARIETY ,
    "Reality Show"             => $VARIETY ,
    "Emission politique"             => $SOCIAL,
    "Politique"             => $SOCIAL ,    
    "Divers"             => $VARIETY ,            
    "Religião"           => $RELIGION ,
    "Musique"            => $MUSIC ,
    "Fitness"           => $FITNESS ,
    "Sports"           => $SPORT ,
    "Ciclismo"         => $SPORT ,
    "Clip"           => $MUSIC ,
    "Anime"           => $CARTOON ,
    "Humor"           => $COMEDY ,

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
