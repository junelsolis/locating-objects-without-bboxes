# Copyright &copyright 2018 The Board of Trustees of Purdue University.
# All rights reserved.
# 
# This source code is not to be distributed or modified
# without the written permission of Edward J. Delp at Purdue University
# Contact information: ace@ecn.purdue.edu
# =====================================================================

import visdom
import torch
import numbers

from torch.autograd import Variable

class Logger():
    def __init__(self,
                 env_name='main',
                 server='http://localhost'):

        # Visdom setup
        self.client = visdom.Visdom(server=server,
                                    env=env_name,
                                    port=8989)

        # Each of the 'windows' in visdom web panel
        self.viz_train_input_win = None
        self.viz_train_loss_win = None
        self.viz_train_gt_win = None
        self.viz_train_est_win = None
        self.viz_val_input_win = None
        self.viz_val_loss_win = None
        self.viz_val_gt_win = None
        self.viz_val_est_win = None

        # Visdom only supports CPU Tensors
        self.device = torch.device("cpu")

    def train_losses(self, terms, iteration_number, terms_legends=None):
        """Plot a new point of the training losses (scalars) to Visdom.
        All losses will be plotted in the same figure/window.

        :param terms: List of scalar losses.
                      Each element will be a different plot in the y axis.
        :param iteration_number: Value of the x axis in the plot.
        :param terms_legends: Legend of each term.
        """

        # Watch dog
        if terms_legends is not None and \
                len(terms) != len(terms_legends):
            raise ValueError('The number of "terms" and "terms_legends" must be equal, got %s and %s, respectively'
                             % (len(terms), len(terms_legends)))
        if not isinstance(iteration_number, numbers.Number):
            raise ValueError('iteration_number must be a number, got %s'
                             % iteration_number)

        # Make terms CPU Tensors
        curated_terms = []
        for term in terms:
            if isinstance(term, numbers.Number):
                curated_term = torch.tensor([term])
            elif isinstance(term, torch.Tensor):
                curated_term = term
            else:
                raise ValueError('there is a term with an unsupported type'
                                 f'({type(term)}')
            curated_term = term.to(self.device)
            curated_term = curated_term.view(1)
            curated_terms.append(curated_term)

        y = torch.cat(curated_terms).view(1, -1).data
        x = torch.Tensor([iteration_number]).repeat(1, len(terms))
        if terms_legends is None:
            terms_legends = ['Term %s' % t
                             for t in range(1, len(terms) + 1)]

        # Send training loss to Visdom
        self.win_train_loss = \
            self.client.updateTrace(Y=y,
                                    X=x,
                                    opts=dict(title='Training',
                                              legend=terms_legends,
                                              ylabel='Loss',
                                              xlabel='Epoch'),
                                    append=True,
                                    win='train_losses')
        if self.win_train_loss == 'win does not exist':
            self.win_train_loss = \
                self.client.line(Y=y,
                                 X=x,
                                 opts=dict(title='Training',
                                           legend=terms_legends,
                                           ylabel='Loss',
                                           xlabel='Epoch'),
                                 win='train_losses')

    def image(self, imgs, titles, window_ids):
        """Send images to Visdom.
        Each image will be shown in a different window/plot.

        :param imgs: List of numpy images.
        :param titles: List of titles of each image.
        :param window_ids: List of window IDs.
        """

        # Watchdog
        if not(len(imgs) == len(titles) == len(window_ids)):
            raise ValueError('The number of "imgs", "titles" and '
                             '"window_ids" must be equal, got '
                             '%s, %s and %s, respectively'
                             % (len(imgs), len(titles), len(window_ids)))

        for img, title, win in zip(imgs, titles, window_ids):
            self.client.image(img,
                              opts=dict(title=title),
                              win=str(win))

    def val_losses(self, terms, iteration_number, terms_legends=None):
        """Plot a new point of the training losses (scalars) to Visdom.  All losses will be plotted in the same figure/window.

        :param terms: List of scalar losses.
                      Each element will be a different plot in the y axis.
        :param iteration_number: Value of the x axis in the plot.
        :param terms_legends: Legend of each term.
        """

        # Watchdog
        if terms_legends is not None and \
                len(terms) != len(terms_legends):
            raise ValueError('The number of "terms" and "terms_legends" must be equal, got %s and %s, respectively'
                             % (len(terms), len(terms_legends)))
        if not isinstance(iteration_number, numbers.Number):
            raise ValueError('iteration_number must be a number, got %s'
                             % iteration_number)

        # Make terms CPU Tensors
        curated_terms = []
        for term in terms:
            if isinstance(term, numbers.Number):
                curated_term = torch.tensor([term])
            elif isinstance(term, torch.Tensor):
                curated_term = term
            else:
                raise ValueError('there is a term with an unsupported type'
                                 f'({type(term)}')
            curated_term = curated_term.to(self.device)
            curated_term = curated_term.view(1)
            curated_terms.append(curated_term)

        y = torch.stack(curated_terms).view(1, -1)
        x = torch.Tensor([iteration_number]).repeat(1, len(terms))
        if terms_legends is None:
            terms_legends = ['Term %s' % t for t in range(1, len(terms) + 1)]

        # Send validation loss to Visdom
        self.win_val_loss = \
            self.client.updateTrace(Y=y,
                                    X=x,
                                    opts=dict(title='Validation',
                                              legend=terms_legends,
                                              ylabel='Loss',
                                              xlabel='Epoch'),
                                    append=True,
                                    win='val_metrics')
        if self.win_val_loss == 'win does not exist':
            self.win_val_loss = \
                self.client.line(Y=y,
                                 X=x,
                                 opts=dict(title='Validation',
                                           legend=terms_legends,
                                           ylabel='Loss',
                                           xlabel='Epoch'),
                                 win='val_metrics')
