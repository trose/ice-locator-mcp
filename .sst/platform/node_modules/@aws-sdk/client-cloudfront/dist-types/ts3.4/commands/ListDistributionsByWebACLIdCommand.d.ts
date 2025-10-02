import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  ListDistributionsByWebACLIdRequest,
  ListDistributionsByWebACLIdResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface ListDistributionsByWebACLIdCommandInput
  extends ListDistributionsByWebACLIdRequest {}
export interface ListDistributionsByWebACLIdCommandOutput
  extends ListDistributionsByWebACLIdResult,
    __MetadataBearer {}
export declare class ListDistributionsByWebACLIdCommand extends $Command<
  ListDistributionsByWebACLIdCommandInput,
  ListDistributionsByWebACLIdCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: ListDistributionsByWebACLIdCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: ListDistributionsByWebACLIdCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<
    ListDistributionsByWebACLIdCommandInput,
    ListDistributionsByWebACLIdCommandOutput
  >;
  private serialize;
  private deserialize;
}
