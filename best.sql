PGDMP     2                    {           best_seller    14.5    14.5 <    6           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            7           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            8           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            9           1262    81927    best_seller    DATABASE     g   CREATE DATABASE best_seller WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'French_France.1252';
    DROP DATABASE best_seller;
                postgres    false            �            1259    81938    clients    TABLE     0  CREATE TABLE public.clients (
    client_id bigint NOT NULL,
    nom character varying(50) NOT NULL,
    prenom character varying(50) NOT NULL,
    adresse character varying(100) NOT NULL,
    telephone character varying(20) NOT NULL,
    email character varying(50) DEFAULT 'none'::character varying
);
    DROP TABLE public.clients;
       public         heap    postgres    false            �            1259    81937    clients_client_id_seq    SEQUENCE     �   CREATE SEQUENCE public.clients_client_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public.clients_client_id_seq;
       public          postgres    false    212            :           0    0    clients_client_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public.clients_client_id_seq OWNED BY public.clients.client_id;
          public          postgres    false    211            �            1259    98323    etat_facture    TABLE     I  CREATE TABLE public.etat_facture (
    facture_id integer,
    etat_id integer NOT NULL,
    etat character varying(50),
    livreur_id integer,
    heure_depart time without time zone,
    heure_arrive time without time zone,
    heure_generation_qr timestamp without time zone,
    heure_scan_qr timestamp without time zone
);
     DROP TABLE public.etat_facture;
       public         heap    postgres    false            �            1259    98322    etat_facture_etat_id_seq    SEQUENCE     �   CREATE SEQUENCE public.etat_facture_etat_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.etat_facture_etat_id_seq;
       public          postgres    false    222            ;           0    0    etat_facture_etat_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.etat_facture_etat_id_seq OWNED BY public.etat_facture.etat_id;
          public          postgres    false    221            �            1259    81966    factures    TABLE     �   CREATE TABLE public.factures (
    facture_id integer NOT NULL,
    client_id bigint,
    date_facture date NOT NULL,
    montant numeric(10,2) NOT NULL,
    lieu_livraison character varying(100),
    livre boolean
);
    DROP TABLE public.factures;
       public         heap    postgres    false            �            1259    81965    factures_facture_id_seq    SEQUENCE     �   CREATE SEQUENCE public.factures_facture_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.factures_facture_id_seq;
       public          postgres    false    216            <           0    0    factures_facture_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.factures_facture_id_seq OWNED BY public.factures.facture_id;
          public          postgres    false    215            �            1259    81957    livreurs    TABLE     t  CREATE TABLE public.livreurs (
    livreur_id integer NOT NULL,
    nom character varying(50) NOT NULL,
    prenom character varying(50) NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(50) NOT NULL,
    quartier_livraison character varying(50) NOT NULL,
    disponible boolean DEFAULT true,
    nombre_livraisons integer DEFAULT 0
);
    DROP TABLE public.livreurs;
       public         heap    postgres    false            �            1259    81956    livreurs_livreur_id_seq    SEQUENCE     �   CREATE SEQUENCE public.livreurs_livreur_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.livreurs_livreur_id_seq;
       public          postgres    false    214            =           0    0    livreurs_livreur_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.livreurs_livreur_id_seq OWNED BY public.livreurs.livreur_id;
          public          postgres    false    213            �            1259    81994    produits    TABLE     �   CREATE TABLE public.produits (
    produit_id integer NOT NULL,
    nom_produit character varying(255) NOT NULL,
    description_produit text,
    prix_produit numeric(10,2),
    quantite integer,
    vendeur_id integer,
    categorie text
);
    DROP TABLE public.produits;
       public         heap    postgres    false            �            1259    90125    produits_image    TABLE     �   CREATE TABLE public.produits_image (
    image_id integer NOT NULL,
    produit_id integer,
    image character varying(200)
);
 "   DROP TABLE public.produits_image;
       public         heap    postgres    false            �            1259    90124    produits_image_image_id_seq    SEQUENCE     �   CREATE SEQUENCE public.produits_image_image_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 2   DROP SEQUENCE public.produits_image_image_id_seq;
       public          postgres    false    220            >           0    0    produits_image_image_id_seq    SEQUENCE OWNED BY     [   ALTER SEQUENCE public.produits_image_image_id_seq OWNED BY public.produits_image.image_id;
          public          postgres    false    219            �            1259    81993    produits_produit_id_seq    SEQUENCE     �   CREATE SEQUENCE public.produits_produit_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.produits_produit_id_seq;
       public          postgres    false    218            ?           0    0    produits_produit_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.produits_produit_id_seq OWNED BY public.produits.produit_id;
          public          postgres    false    217            �            1259    81929    vendeurs    TABLE     �   CREATE TABLE public.vendeurs (
    vendeur_id integer NOT NULL,
    username character varying(50) NOT NULL,
    prenom character varying(50) NOT NULL,
    nom character varying(50) NOT NULL,
    password character varying(50) NOT NULL
);
    DROP TABLE public.vendeurs;
       public         heap    postgres    false            �            1259    81928    vendeurs_vendeur_id_seq    SEQUENCE     �   CREATE SEQUENCE public.vendeurs_vendeur_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 .   DROP SEQUENCE public.vendeurs_vendeur_id_seq;
       public          postgres    false    210            @           0    0    vendeurs_vendeur_id_seq    SEQUENCE OWNED BY     S   ALTER SEQUENCE public.vendeurs_vendeur_id_seq OWNED BY public.vendeurs.vendeur_id;
          public          postgres    false    209            {           2604    98339    clients client_id    DEFAULT     v   ALTER TABLE ONLY public.clients ALTER COLUMN client_id SET DEFAULT nextval('public.clients_client_id_seq'::regclass);
 @   ALTER TABLE public.clients ALTER COLUMN client_id DROP DEFAULT;
       public          postgres    false    211    212    212            �           2604    98326    etat_facture etat_id    DEFAULT     |   ALTER TABLE ONLY public.etat_facture ALTER COLUMN etat_id SET DEFAULT nextval('public.etat_facture_etat_id_seq'::regclass);
 C   ALTER TABLE public.etat_facture ALTER COLUMN etat_id DROP DEFAULT;
       public          postgres    false    222    221    222            �           2604    81969    factures facture_id    DEFAULT     z   ALTER TABLE ONLY public.factures ALTER COLUMN facture_id SET DEFAULT nextval('public.factures_facture_id_seq'::regclass);
 B   ALTER TABLE public.factures ALTER COLUMN facture_id DROP DEFAULT;
       public          postgres    false    216    215    216            }           2604    81960    livreurs livreur_id    DEFAULT     z   ALTER TABLE ONLY public.livreurs ALTER COLUMN livreur_id SET DEFAULT nextval('public.livreurs_livreur_id_seq'::regclass);
 B   ALTER TABLE public.livreurs ALTER COLUMN livreur_id DROP DEFAULT;
       public          postgres    false    214    213    214            �           2604    81997    produits produit_id    DEFAULT     z   ALTER TABLE ONLY public.produits ALTER COLUMN produit_id SET DEFAULT nextval('public.produits_produit_id_seq'::regclass);
 B   ALTER TABLE public.produits ALTER COLUMN produit_id DROP DEFAULT;
       public          postgres    false    217    218    218            �           2604    90128    produits_image image_id    DEFAULT     �   ALTER TABLE ONLY public.produits_image ALTER COLUMN image_id SET DEFAULT nextval('public.produits_image_image_id_seq'::regclass);
 F   ALTER TABLE public.produits_image ALTER COLUMN image_id DROP DEFAULT;
       public          postgres    false    220    219    220            z           2604    81932    vendeurs vendeur_id    DEFAULT     z   ALTER TABLE ONLY public.vendeurs ALTER COLUMN vendeur_id SET DEFAULT nextval('public.vendeurs_vendeur_id_seq'::regclass);
 B   ALTER TABLE public.vendeurs ALTER COLUMN vendeur_id DROP DEFAULT;
       public          postgres    false    210    209    210            )          0    81938    clients 
   TABLE DATA           T   COPY public.clients (client_id, nom, prenom, adresse, telephone, email) FROM stdin;
    public          postgres    false    212   'I       3          0    98323    etat_facture 
   TABLE DATA           �   COPY public.etat_facture (facture_id, etat_id, etat, livreur_id, heure_depart, heure_arrive, heure_generation_qr, heure_scan_qr) FROM stdin;
    public          postgres    false    222   J       -          0    81966    factures 
   TABLE DATA           g   COPY public.factures (facture_id, client_id, date_facture, montant, lieu_livraison, livre) FROM stdin;
    public          postgres    false    216   �J       +          0    81957    livreurs 
   TABLE DATA           �   COPY public.livreurs (livreur_id, nom, prenom, username, password, quartier_livraison, disponible, nombre_livraisons) FROM stdin;
    public          postgres    false    214   �K       /          0    81994    produits 
   TABLE DATA              COPY public.produits (produit_id, nom_produit, description_produit, prix_produit, quantite, vendeur_id, categorie) FROM stdin;
    public          postgres    false    218   �M       1          0    90125    produits_image 
   TABLE DATA           E   COPY public.produits_image (image_id, produit_id, image) FROM stdin;
    public          postgres    false    220   �O       '          0    81929    vendeurs 
   TABLE DATA           O   COPY public.vendeurs (vendeur_id, username, prenom, nom, password) FROM stdin;
    public          postgres    false    210   �O       A           0    0    clients_client_id_seq    SEQUENCE SET     C   SELECT pg_catalog.setval('public.clients_client_id_seq', 5, true);
          public          postgres    false    211            B           0    0    etat_facture_etat_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.etat_facture_etat_id_seq', 17, true);
          public          postgres    false    221            C           0    0    factures_facture_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.factures_facture_id_seq', 4, true);
          public          postgres    false    215            D           0    0    livreurs_livreur_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.livreurs_livreur_id_seq', 2, true);
          public          postgres    false    213            E           0    0    produits_image_image_id_seq    SEQUENCE SET     I   SELECT pg_catalog.setval('public.produits_image_image_id_seq', 8, true);
          public          postgres    false    219            F           0    0    produits_produit_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.produits_produit_id_seq', 50, true);
          public          postgres    false    217            G           0    0    vendeurs_vendeur_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.vendeurs_vendeur_id_seq', 4, true);
          public          postgres    false    209            �           2606    98341    clients clients_pkey 
   CONSTRAINT     Y   ALTER TABLE ONLY public.clients
    ADD CONSTRAINT clients_pkey PRIMARY KEY (client_id);
 >   ALTER TABLE ONLY public.clients DROP CONSTRAINT clients_pkey;
       public            postgres    false    212            �           2606    98328    etat_facture etat_facture_pkey 
   CONSTRAINT     a   ALTER TABLE ONLY public.etat_facture
    ADD CONSTRAINT etat_facture_pkey PRIMARY KEY (etat_id);
 H   ALTER TABLE ONLY public.etat_facture DROP CONSTRAINT etat_facture_pkey;
       public            postgres    false    222            �           2606    81971    factures factures_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.factures
    ADD CONSTRAINT factures_pkey PRIMARY KEY (facture_id);
 @   ALTER TABLE ONLY public.factures DROP CONSTRAINT factures_pkey;
       public            postgres    false    216            �           2606    81962    livreurs livreurs_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.livreurs
    ADD CONSTRAINT livreurs_pkey PRIMARY KEY (livreur_id);
 @   ALTER TABLE ONLY public.livreurs DROP CONSTRAINT livreurs_pkey;
       public            postgres    false    214            �           2606    81964    livreurs livreurs_username_key 
   CONSTRAINT     ]   ALTER TABLE ONLY public.livreurs
    ADD CONSTRAINT livreurs_username_key UNIQUE (username);
 H   ALTER TABLE ONLY public.livreurs DROP CONSTRAINT livreurs_username_key;
       public            postgres    false    214            �           2606    90130 "   produits_image produits_image_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.produits_image
    ADD CONSTRAINT produits_image_pkey PRIMARY KEY (image_id);
 L   ALTER TABLE ONLY public.produits_image DROP CONSTRAINT produits_image_pkey;
       public            postgres    false    220            �           2606    82001    produits produits_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.produits
    ADD CONSTRAINT produits_pkey PRIMARY KEY (produit_id);
 @   ALTER TABLE ONLY public.produits DROP CONSTRAINT produits_pkey;
       public            postgres    false    218            �           2606    81934    vendeurs vendeurs_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.vendeurs
    ADD CONSTRAINT vendeurs_pkey PRIMARY KEY (vendeur_id);
 @   ALTER TABLE ONLY public.vendeurs DROP CONSTRAINT vendeurs_pkey;
       public            postgres    false    210            �           2606    81936    vendeurs vendeurs_username_key 
   CONSTRAINT     ]   ALTER TABLE ONLY public.vendeurs
    ADD CONSTRAINT vendeurs_username_key UNIQUE (username);
 H   ALTER TABLE ONLY public.vendeurs DROP CONSTRAINT vendeurs_username_key;
       public            postgres    false    210            �           2606    98329 )   etat_facture etat_facture_facture_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.etat_facture
    ADD CONSTRAINT etat_facture_facture_id_fkey FOREIGN KEY (facture_id) REFERENCES public.factures(facture_id);
 S   ALTER TABLE ONLY public.etat_facture DROP CONSTRAINT etat_facture_facture_id_fkey;
       public          postgres    false    222    216    3215            �           2606    114688 )   etat_facture etat_facture_livreur_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.etat_facture
    ADD CONSTRAINT etat_facture_livreur_id_fkey FOREIGN KEY (livreur_id) REFERENCES public.livreurs(livreur_id);
 S   ALTER TABLE ONLY public.etat_facture DROP CONSTRAINT etat_facture_livreur_id_fkey;
       public          postgres    false    3211    214    222            �           2606    98351     factures factures_client_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.factures
    ADD CONSTRAINT factures_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.clients(client_id);
 J   ALTER TABLE ONLY public.factures DROP CONSTRAINT factures_client_id_fkey;
       public          postgres    false    216    3209    212            �           2606    90131 -   produits_image produits_image_produit_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.produits_image
    ADD CONSTRAINT produits_image_produit_id_fkey FOREIGN KEY (produit_id) REFERENCES public.produits(produit_id) ON DELETE CASCADE;
 W   ALTER TABLE ONLY public.produits_image DROP CONSTRAINT produits_image_produit_id_fkey;
       public          postgres    false    218    3217    220            �           2606    82002 !   produits produits_vendeur_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.produits
    ADD CONSTRAINT produits_vendeur_id_fkey FOREIGN KEY (vendeur_id) REFERENCES public.vendeurs(vendeur_id);
 K   ALTER TABLE ONLY public.produits DROP CONSTRAINT produits_vendeur_id_fkey;
       public          postgres    false    3205    218    210            )   �   x�m�AK�0�ϓ_�](m�6�V\� ���v��LI�B��*(��y�7�)�'��:�+<����RuS�'o��~���<Bg���D	��w��1��㒗�����C�h�p����
�Lt&@o�t�a<Q��HΛ�\�qn!�.x ���Jq.�n�Te���]��
��<W?[�fl��h��@G&�P�nJx�mS��&?<�Nք��������v<�u_/c��Q_�      3   �   x�}Q[
�@���$���'�(~���=���,� KHf&�����]�	�;��孅4��	`J}&�W̍O?C�y��sB�Wc��vPP;�8� �|�b�П�ͪUV�IG㸭s�I�et�/ �>l�Iێ�|���t��dŘ�a���_I}L��8��c����AW�m�oŎ����Rd9+�;l�c~���      -   �   x�m�;�0�Z>HF�_%��Q�Ӥ��L��(���߬��H�Ej�ȳ����$�42��7���^qD��J�Ｌ��r8��2�����ɂel��^�HJ�<[�b�[y�LaD#��^7*����v?�i_Դ�Lu�K���*�p��we��J_��­
,�UaYp����p-Ee=F���{�k      +   �  x�mS���0=�|E���&�p�n�BՖ����VCp�!��/Z��㰛4����h�g�;�&������f�� �0��j"��R&i�����W�����R�9���(��B�8��TU'붌�/O���}�2LD������iA�ʼS�afM�!��e��"Ƕ����}Ȝ!2��Hf��F���@`4��h��
Z(쩣�~o�Ys�_���
�2���8����$]k�Θ�+l��9Z�72�Hp�K��Eem���I:�)���L7Yz��`�bB ��GEDBb�+�G�qR�H'��}�H��њ?9��������u�?v���<�u��a���˪�ߔ3d��e���?�C��m1�ڟ�A�T�N������x�*Ž���ߴ��}[��M�n�B�<���6�(��i���`�r�	V6��T[�oN��9q#˗`F^9���@lZD������������-��zks����sE� u�NG      /   �  x���Kr�0���)� )� ��:��T��l4�m3#���hr_l����`V*Z���%	�|QMU5+8"T������'Z�Ϝ��i,\LQ`�d�O�qμ/'��4:���>Ϸ?vN��]�p���2�W�������R����e��0����8
�`�	�B��\eY�uVCE&G3�P��V���9����U%z���S��o�r�K���`Y��7�"����S^�ӋN/�ZĤ����I��K2�#\��@�gu��Bm�U5�PZUg��a����9��L^���Fa��[KG�P��F���Z�OL�����R�
5�F�&���#�h�k ����~�y��C�����KN���;ّ����b"��!<V[C��C��3T��p5yS ��O��C:��h�"8�}>�|�B>�k�Ct9S����?�ՒP7x��ó�#Ujdi��t�u�D��z�/�ht1���+��Ɉ�G���H����ԕ���A�*}vA�����/D���      1   2   x�3�44���MLO5��*H�2��-�|c8��7���|3�<DA� ���      '   g   x�3����ȋO�O��28]���������C#c.sCCs3Kcάļ����̒N/ �3̄�515�2�,KM)����ҙ@5.���y9��@�L�b���� �-"�     