from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.articles.models import Article, Categorie, Tag, Comments
from django.utils import timezone


class Command(BaseCommand):
    help = 'Peuple la base de données avec des données de démonstration'

    def handle(self, *args, **options):
        # Superuser
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@lemedia.ht', 'admin1234')
            self.stdout.write(self.style.SUCCESS('Superutilisateur "admin" créé (mdp: admin1234)'))
        else:
            admin = User.objects.get(username='admin')

        # Journaliste
        if not User.objects.filter(username='journaliste').exists():
            journaliste = User.objects.create_user('journaliste', 'journaliste@lemedia.ht', 'journaliste1234',
                                                    first_name='Marie', last_name='Dupont')
            self.stdout.write(self.style.SUCCESS('Utilisateur "journaliste" créé'))
        else:
            journaliste = User.objects.get(username='journaliste')

        # Ajouter journaliste au groupe
        from django.contrib.auth.models import Group, Permission
        from django.contrib.contenttypes.models import ContentType
        from apps.articles.models import Article as Art
        groupe, _ = Group.objects.get_or_create(name='Journalistes')
        ct = ContentType.objects.get_for_model(Art)
        for perm in Permission.objects.filter(content_type=ct):
            groupe.permissions.add(perm)
        journaliste.groups.add(groupe)

        # Catégories
        categories_data = [
            ('Politique', 'politique', '#e63946'),
            ('Économie', 'economie', '#2a9d8f'),
            ('Culture', 'culture', '#e9c46a'),
            ('Sport', 'sport', '#f4a261'),
            ('Technologie', 'technologie', '#457b9d'),
            ('Société', 'societe', '#6a4c93'),
        ]
        categories = {}
        for nom, slug, couleur in categories_data:
            cat, _ = Categorie.objects.get_or_create(slug=slug, defaults={'nom': nom, 'couleur': couleur})
            categories[slug] = cat
        self.stdout.write(self.style.SUCCESS(f'{len(categories)} catégories créées'))

        # Tags
        tags_data = ['Haiti', 'International', 'Développement', 'Jeunesse', 'Environnement', 'Santé']
        tags = {}
        for nom in tags_data:
            from django.utils.text import slugify
            tag, _ = Tag.objects.get_or_create(slug=slugify(nom), defaults={'nom': nom})
            tags[nom] = tag

        # Articles
        articles_data = [
            {
                'titre': 'Les nouvelles politiques économiques transforment le paysage haïtien',
                'resume': 'Une série de réformes économiques majeures est en cours de discussion au parlement, promettant de redéfinir la structure financière du pays.',
                'contenu': '''Le gouvernement haïtien a présenté cette semaine un ensemble de réformes économiques ambitieuses visant à moderniser l\'infrastructure financière du pays et à attirer des investissements étrangers.

Ces mesures comprennent la révision du code des impôts, la simplification des procédures d\'enregistrement des entreprises et la création de zones économiques spéciales dans plusieurs régions du pays.

Les experts économiques saluent ces initiatives tout en soulignant la nécessité d\'une mise en œuvre rigoureuse. "Les réformes proposées vont dans le bon sens, mais leur succès dépendra de la volonté politique et des capacités institutionnelles," a déclaré un économiste de l\'Université d\'État d\'Haïti.

Le secteur privé a globalement bien accueilli ces annonces, notant que certaines de ces mesures étaient demandées depuis plusieurs années. Les chambres de commerce ont exprimé leur soutien, tout en appelant à un dialogue continu avec les autorités.

Les partenaires internationaux du développement, dont la Banque mondiale et le FMI, ont indiqué qu\'ils suivaient ces évolutions avec intérêt et étaient prêts à apporter leur soutien technique.''',
                'categorie': categories['politique'],
                'en_une': True,
                'auteur': admin,
                'image_url': 'https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80',
            },
            {
                'titre': 'Le secteur agricole en pleine mutation : vers une modernisation durable',
                'resume': 'De nouveaux programmes d\'agriculture durable sont déployés à travers le pays pour renforcer la sécurité alimentaire et améliorer les revenus des agriculteurs.',
                'contenu': '''L\'agriculture haïtienne connaît une transformation significative grâce à l\'introduction de nouvelles techniques et technologies qui promettent d\'améliorer la productivité tout en préservant l\'environnement.

Des organisations non gouvernementales, en partenariat avec le ministère de l\'Agriculture, ont lancé plusieurs programmes pilotes dans les départements du Nord, de l\'Artibonite et du Sud. Ces initiatives couvrent l\'irrigation intelligente, l\'utilisation d\'intrants biologiques et la formation des agriculteurs aux pratiques agroécologiques.

Les résultats préliminaires sont encourageants : dans les zones pilotes, on observe une augmentation de 30 à 40% des rendements pour certaines cultures, accompagnée d\'une réduction significative de l\'utilisation de pesticides chimiques.

"Ces changements ne se font pas du jour au lendemain, mais nous voyons déjà une différence dans nos récoltes," témoigne un agriculteur de l\'Artibonite. "La formation reçue nous a ouvert les yeux sur des méthodes que nos ancêtres utilisaient et que nous avions oubliées."

L\'objectif à long terme est de réduire la dépendance aux importations alimentaires et de positionner Haïti comme un exportateur de produits agricoles de qualité dans la région caribéenne.''',
                'categorie': categories['economie'],
                'en_une': True,
                'auteur': journaliste,
                'image_url': 'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=800&q=80',
            },
            {
                'titre': 'Festival de jazz de Port-au-Prince : une édition exceptionnelle',
                'resume': 'La 15e édition du Festival International de Jazz de Port-au-Prince a réuni des artistes de renom venus de quatre continents.',
                'contenu': '''La capitale haïtienne a vibré au son du jazz pendant cinq jours mémorables. La 15e édition du Festival International de Jazz de Port-au-Prince a confirmé sa place comme l\'un des événements culturels les plus importants de la Caraïbe.

Avec plus de 50 artistes venus de 20 pays différents, le festival a proposé une programmation éclectique mêlant jazz traditionnel, fusion afro-caribéenne et expérimentations contemporaines. Les concerts au Champ de Mars et dans plusieurs venues de la ville ont attiré des milliers de spectateurs.

La soirée d\'ouverture, avec le légendaire pianiste américain Marcus Roberts, a posé le ton d\'une édition placée sous le signe de l\'excellence et de l\'échange culturel. La collaboration entre artistes haïtiens et internationaux a donné naissance à des moments musicaux inoubliables.

Le directeur artistique du festival se dit satisfait : "Chaque année, nous cherchons à créer des ponts entre les cultures. Cette édition a parfaitement illustré la capacité de la musique à transcender les frontières."

Les retombées économiques et touristiques du festival sont significatives, avec un taux d\'occupation hôtelier record et une augmentation des visites dans les sites culturels et historiques de la ville.''',
                'categorie': categories['culture'],
                'en_une': True,
                'auteur': journaliste,
                'image_url': 'https://images.unsplash.com/photo-1511192336575-5a79af67a629?w=800&q=80',
            },
            {
                'titre': 'L\'équipe nationale de football qualifiée pour les demi-finales',
                'resume': 'Une victoire historique contre la Jamaïque propulse les Grenadiers vers les demi-finales du championnat de la CONCACAF.',
                'contenu': '''Dans un match d\'anthologie disputé devant 35 000 spectateurs en délire, l\'équipe nationale de football d\'Haïti a réalisé l\'exploit de battre la Jamaïque 3-1, s\'assurant une place historique en demi-finale du championnat de la CONCACAF.

Les buts ont été inscrits par Duckens Nazon, auteur d\'un doublé, et Frantzdy Pierrot, dont la frappe magistrale a scellé le sort du match à la 78e minute. Le gardien Johnny Placide a réalisé plusieurs arrêts décisifs qui ont maintenu le score en faveur des Grenadiers.

"C\'est le fruit de plusieurs années de travail et de sacrifices," a déclaré le sélectionneur national après la rencontre. "Ces joueurs ont donné tout ce qu\'ils avaient pour leur pays."

La nouvelle s\'est répandue comme une traînée de poudre à travers le pays, provoquant des scènes de liesse populaire dans les rues des principales villes. Le président de la Fédération Haïtienne de Football a félicité l\'équipe et a promis une prime spéciale aux joueurs.

Les Grenadiers affrontent désormais le Mexique en demi-finale, un défi de taille mais que les supporters haïtiens abordent avec une confiance renouvelée.''',
                'categorie': categories['sport'],
                'en_une': False,
                'auteur': admin,
                'image_url': 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800&q=80',
            },
            {
                'titre': 'La révolution numérique change le quotidien des Haïtiens',
                'resume': 'L\'essor des services mobiles et des fintech transforme rapidement l\'accès aux services financiers et au commerce pour des milliers de citoyens.',
                'contenu': '''La transformation numérique s\'accélère en Haïti, portée par l\'adoption massive des smartphones et le développement de services innovants adaptés aux réalités locales.

Les applications de mobile money connaissent une croissance exponentielle, permettant à des personnes non bancarisées d\'accéder pour la première fois à des services financiers. On estime que plus de 2 millions de Haïtiens utilisent aujourd\'hui ces services pour envoyer de l\'argent, payer des factures et effectuer des achats.

Le commerce électronique local se développe également, avec l\'émergence de plateformes haïtiennes de vente en ligne qui proposent des produits locaux et facilitent la livraison à domicile. Ces initiatives créent de nouveaux emplois et ouvrent des marchés aux petits producteurs et artisans.

"Avant, je devais me déplacer jusqu\'en ville pour vendre mes produits. Maintenant, j\'ai des clients dans tout le pays," témoigne une artisane de Jacmel qui vend ses créations via une application locale.

Le défi majeur reste l\'accès à internet, encore limité dans les zones rurales. Des projets d\'infrastructure sont en cours pour étendre la couverture réseau et réduire la fracture numérique entre villes et campagnes.''',
                'categorie': categories['technologie'],
                'en_une': False,
                'auteur': journaliste,
                'image_url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800&q=80',
            },
            {
                'titre': 'Éducation : des initiatives citoyennes comblent les lacunes du système',
                'resume': 'Face aux défis du secteur éducatif, des citoyens engagés créent des solutions innovantes pour améliorer l\'accès à l\'éducation de qualité.',
                'contenu': '''Face aux difficultés chroniques du système éducatif haïtien, une nouvelle génération d\'entrepreneurs sociaux et de citoyens engagés prend les choses en main avec des approches novatrices et des résultats concrets.

Des bibliothèques communautaires numériques ont été installées dans plusieurs quartiers défavorisés, offrant un accès gratuit à des milliers de livres et ressources pédagogiques. Ces espaces deviennent rapidement des centres d\'apprentissage prisés par les jeunes.

Des programmes de mentorat connectent des professionnels établis avec des lycéens en difficulté, leur fournissant orientation, conseils et parfois même un appui financier pour poursuivre leurs études. Les résultats se mesurent en taux de réussite au baccalauréat nettement supérieurs dans les zones couvertes.

Une initiative particulièrement remarquée est le programme "École du samedi", qui propose des cours de rattrapage et des activités parascolaires gratuites dans les écoles publiques. Animés par des étudiants universitaires bénévoles, ces cours touchent plus de 5 000 élèves chaque semaine dans la seule zone métropolitaine.

"Nous ne pouvons pas attendre que l\'État résolve tous les problèmes. Chacun de nous a un rôle à jouer dans l\'éducation de nos enfants," affirme la fondatrice d\'une de ces initiatives.''',
                'categorie': categories['societe'],
                'en_une': False,
                'auteur': admin,
                'image_url': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=800&q=80',
            },
        ]

        for i, data in enumerate(articles_data):
            if not Article.objects.filter(titre=data['titre']).exists():
                article = Article.objects.create(
                    **data,
                    statut='publie',
                    date_publication=timezone.now(),
                    vues=(i + 1) * 150 - i * 30,
                )
                # Add tags
                if i < 3:
                    article.tags.add(tags['Haiti'], tags['International'])
                else:
                    article.tags.add(tags['Développement'], tags['Jeunesse'])

        # Commentaires
        article_exemple = Article.objects.filter(statut='publie').first()
        if article_exemple and not Comments.objects.filter(article=article_exemple).exists():
            Comments.objects.create(
                article=article_exemple, auteur=journaliste, approuve=True,
                contenu="Excellent article, très bien documenté ! Cette analyse apporte un éclairage précieux sur la situation actuelle."
            )
            Comments.objects.create(
                article=article_exemple, auteur=admin, approuve=True,
                contenu="Merci pour ce compte-rendu détaillé. Il est important que les citoyens soient informés de ces développements."
            )

        self.stdout.write(self.style.SUCCESS(f'✓ Données de démonstration créées avec succès !'))
        self.stdout.write(self.style.WARNING('Admin: admin / admin1234'))
        self.stdout.write(self.style.WARNING('Journaliste: journaliste / journaliste1234'))
